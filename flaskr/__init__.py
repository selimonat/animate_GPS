from flask import Flask, render_template, request

from Radar import RadarView
import os
import logging
import threading


def thread_function(filename):
    logging.info('Inside thread_function')
    r = RadarView(filename)
    r.save_radar_html()
    r.get_frames()
    r.get_video()
    logging.info('Thread_function finished.')


app = Flask(__name__)


@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        folder = os.path.join("webdata", f.filename)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        filename = os.path.join("webdata", f.filename,f.filename)
        logging.info(f"Saving file as {filename}.")
        f.save(filename)

        logging.info(f"Starting conversion thread.")
        x = threading.Thread(target=thread_function, args=(filename,))
        x.start()

        return 'file uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)