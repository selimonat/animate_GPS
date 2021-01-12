from flask import Flask, render_template, request

from Radar import RadarView
import os
import logging
import threading
import numpy as np


def thread_function(filename):
    logging.info('Inside thread_function')
    r = RadarView(filename)
    r.save_radar_html()
    r.get_frames()
    r.get_video()
    logging.info('Thread_function finished.')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/upload')
    def upload_file():
        session_id = np.random
        return render_template('upload.html')


    @app.route('/uploader', methods=['GET', 'POST'])
    def uploader():
        if request.method == 'POST':
            f = request.files['file']
            folder = os.path.join("webdata", f.filename)
            if not os.path.isdir(folder):
                os.mkdir(folder)
            filename = os.path.join("webdata", f.filename, f.filename)
            logging.info(f"Saving file as {filename}.")
            f.save(filename)

            logging.info(f"Starting conversion thread.")
            x = threading.Thread(target=thread_function, args=(filename,))
            x.start()

            return 'file uploaded successfully'

    return app

if __name__ == '__main__':
    app.run(debug=True)