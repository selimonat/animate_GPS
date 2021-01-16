from flask import Flask, render_template, request, url_for

from Radar.Radar import RadarView
import os
import logging
import threading
import numpy as np
from flask_socketio import SocketIO, emit
import db
from threading import Thread, Event

test_config = None

thread = Thread()
thread_stop_event = Event()


# create a Flask app
app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),)

if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

db.init_app(app)

# ensure the instance folder exists
try:
    print(app.instance_path)
    os.makedirs(app.instance_path)
except OSError:
    pass

# turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)


def thread_function(filename):
    logging.info('Inside thread_function')
    r = RadarView(filename)
    socketio.emit('thread_function', {'step': 0}, namespace='/test')
    r.save_radar_html()
    socketio.emit('thread_function', {'step': 1}, namespace='/test')
    r.get_frames()
    socketio.emit('thread_function', {'step': 2}, namespace='/test')
    r.get_video()
    socketio.emit('thread_function', {'step': 3}, namespace='/test')
    socketio.emit('thread_function', {'step': "<a href=http://localhost:5000>bla</a>"}, namespace='/test')



@app.route('/')
def landing_page():

    return "This is your landing page and you can upload a file from <a href=http://localhost:5000" + url_for(
        'upload_file') + "> here </a>"


@app.route('/upload')
def upload_file():

    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global thread
    if request.method == 'POST':
        f = request.files['file']
        folder = os.path.join("webdata", f.filename)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        filename = os.path.join("webdata", f.filename, f.filename)
        logging.info(f"Saving file as {filename}.")
        f.save(filename)

        logging.info(f"Starting conversion thread.")
        if not thread.isAlive():
            print("Starting Thread")
            thread = socketio.start_background_task(thread_function, filename)

        return render_template('upload.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')


if __name__ == '__main__':
    socketio.run(app)