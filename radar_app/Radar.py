"""
"""
import gpxpy
import sys
import pandas as pd
import os
from Map import Map
import time

from joblib import Parallel, delayed
import logging

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from urllib3.connectionpool import log as urlliblogger
import subprocess

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# Set the threshold for selenium to WARNING
LOGGER.setLevel(logging.WARNING)
# Set the threshold for urllib3 to WARNING
urlliblogger.setLevel(logging.WARNING)


class RadarView:

    def __init__(self, gpx_file):

        self.gpx_file = os.path.abspath(gpx_file)
        # prepare path variables
        self.dirname = os.path.dirname(self.gpx_file)
        self.html_folder = os.path.abspath(os.path.join(self.dirname, "html"))
        self.png_folder = os.path.abspath(os.path.join(self.dirname, "png"))
        # create files if necessary
        if not os.path.isdir(self.html_folder):
            os.mkdir(self.html_folder)
        if not os.path.isdir(self.png_folder):
            os.mkdir(self.png_folder)

        # parse the gpx file
        self.read_file()
        self.df = self.df.loc[:3, slice(None)]
        self.html_files = list()

    def read_file(self):
        # Parse the GPX file

        logging.info('Reading GPX file')
        with open(self.gpx_file, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        logging.info('Converting to Pandas')
        data = list()
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    data.append({'timestamp': point.time,
                                 'lat': point.latitude,
                                 'lon': point.longitude,
                                 'elevation': point.elevation
                                 })
        self.df = pd.DataFrame(data)

    def save_radar_html(self):

        counter = 0
        for lat, lon in zip(self.df.lat, self.df.lon):
            counter += 1
            logging.info(f"Creating HTML files {counter}: {lat},{lon}")
            self.html_files.append(os.path.join(self.html_folder, f"map_{counter :05}.html"))
            map = Map(lat, lon, zoom_start=18)
            map.add_dot_to_map(lat, lon,radius=12)
            map.map.save(self.html_files[-1])

    def _save_png(self, html_file):

        logging.info(f"Converting {html_file} to PNG file.")
        delay = 3
        png_file = os.path.join(self.png_folder, os.path.basename(html_file) + ".png")

        # firefox_options = webdriver.FirefoxOptions()
        # firefox_options.set_headless()

        browser = webdriver.Firefox(log_path="./firefox.log")
        browser.get(f"file://" + html_file)
        # Give the map tiles some time to load
        time.sleep(delay)
        browser.save_screenshot(png_file)
        browser.quit()

    def get_frames(self):

        Parallel(n_jobs=4, prefer="threads")(
            delayed(self._save_png)(H) for H in self.html_files
        )

    def get_video(self):
        logging.info("Creating video.")
        cmd = ["ffmpeg","-loglevel","quiet", "-y", "-framerate", "25", "-pattern_type", "glob", "-i", os.path.join(
            self.png_folder,'*.png'), "-c:v", "libx264", "-r", "30",
               "-pix_fmt", "yuv420p", self.gpx_file + ".mp4"]
        process = subprocess.call(cmd,stdout=subprocess.PIPE, universal_newlines=True)
        return process


if __name__ is "__main__":

    r = RadarView("./test/test_data/test.gpx")
    r.save_radar_html()
    r.get_frames()
    r.get_video()
