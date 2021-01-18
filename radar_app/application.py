"""
Demo Flask application to test the operation of Flask with socket.io

Aim is to create a webpage that is constantly updated with random numbers from a background python process.

30th May 2014

===================

Updated 13th April 2018

+ Upgraded code to Python 3
+ Used Python3 SocketIO implementation
+ Updated CDN Javascript and CSS sources

"""

# Start with a basic flask app webpage.
import os
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, request
from random import random
from time import sleep
from threading import Thread, Event

__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

# turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

# random number Generator Thread
thread = Thread()
thread_stop_event = Event()


def random_number_gen():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    # infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random()*10, 3)
        print(f"Inside random number gen: {number}")
        socketio.emit('progress_report', {'main': number}, namespace='/test')
        socketio.sleep(1)


@app.route('/')
def index():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')


@app.route('/uploader', methods=['POST'])
def uploader():
    global thread
    if request.method == 'POST':
        f = request.files['file']
        folder = os.path.join("webdata", f.filename)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        filename = os.path.join("webdata", f.filename, f.filename)
        print(f"From uploader: Saving file as {filename}.")
        socketio.emit('progress_report', {'main': "File downloaded"}, namespace='/test')
        f.save(filename)

        # Start the random number generator thread only if the thread has not been started before.
        if not thread.isAlive():
            print("Starting Thread")
            socketio.emit('progress_report', {'main': "Conversion starting"}, namespace='/test')
            thread = socketio.start_background_task(random_number_gen)

    return '', 204


@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    # global thread
    print('Client connected.')
    socketio.emit('progress_report', {'main': "Waiting for upload..."}, namespace='/test')


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
