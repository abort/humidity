import os

from flask import Flask, g, redirect, render_template, request, url_for
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from random import randint

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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

    from . import db
    db.init_app(app)

    from flaskr import chart
    app.register_blueprint(chart.bp)
    app.add_url_rule("/", endpoint="index")

    def read_sensors():
        with app.app_context():
            humidity = randint(0, 80)
            temperature = randint(-20, 50)
            d = db.get_db()
            d.execute(
                'INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)',
                (temperature, humidity)
            )
            d.commit()

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(read_sensors, 'interval', minutes=30)
    sched.start()

    return app