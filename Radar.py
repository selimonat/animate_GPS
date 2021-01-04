"""
"""
import gpxpy
import sys
import pandas as pd
import os
from Map import Map
import time
from selenium import webdriver

from joblib import Parallel, delayed
import logging

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class RadarView:

    def __init__(self, gpx_file):

        self.gpx_file = gpx_file
        self.read_file()
        self.df = self.df.loc[:40, slice(None)]
        self.html_files = list()

    def read_file(self):

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
            self.html_files.append(os.path.abspath(f"./tmp_maps/map_{counter :05}.html"))
            map = Map(lat, lon, zoom_start=18)
            map.add_dot_to_map(lat, lon,radius=12)
            map.map.save(self.html_files[-1])

    def _save_png(self, html_file):

        logging.info(f"Converting {html_file} to PNG file.")
        delay = 3
        png_file = os.path.join(html_file + ".png")
        browser = webdriver.Firefox()
        browser.get(f"file://" + html_file)
        # Give the map tiles some time to load
        time.sleep(delay)
        browser.save_screenshot(png_file)
        browser.quit()

    def get_frames(self):

        Parallel(n_jobs=4, prefer="threads")(
            delayed(self._save_png)(H) for H in self.html_files
        )

if __name__ in "__main__":

    r = RadarView("test.gpx")
    r.save_radar_html()
    r.get_frames()