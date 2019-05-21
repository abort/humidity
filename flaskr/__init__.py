import os

from flask import Flask, g, redirect, render_template, request, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from random import randint
import requests
import platform
import io


def is_raspberry_pi(raise_on_errors=False):
    """Checks if Raspberry PI"""
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            found = False
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    found = True
                    label, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value not in (
                        'BCM2708',
                        'BCM2709',
                        'BCM2835',
                        'BCM2836'
                    ):
                        if raise_on_errors:
                            raise ValueError(
                                'This system does not appear to be a '
                                'Raspberry Pi.'
                            )
                        else:
                            return False
            if not found:
                if raise_on_errors:
                    raise ValueError(
                        'Unable to determine if this system is a Raspberry Pi.'
                    )
                else:
                    return False
    except IOError:
        if raise_on_errors:
            raise ValueError('Unable to open `/proc/cpuinfo`.')
        else:
            return False

    return True

def read_sensor_data():
    import Adafruit_DHT
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    return humidity, temperature

def generate_sensor_data():
    humidity = randint(0, 100)
    temperature = randint(-20, 50)
    return humidity, temperature

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

    telegram_enabled = os.environ.get("TELEGRAM_ENABLED", default=False) 
    telegram_token = os.environ.get("TELEGRAM_TOKEN", default=None)
    telegram_chatid = os.environ.get("TELEGRAM_CHATID", default=None)
    polling_interval = int(os.environ.get("POLLING_INTERVAL", default=1800))
    threshold = int(os.environ.get("THRESHOLD", default=40))
    
    app.config['THRESHOLD'] = threshold

    is_pi = is_raspberry_pi()

    print("Running on {}".format("rpi" if is_pi else platform.system()))


    if telegram_enabled:
        if not telegram_token:
            print("Warning: Telegram token not specified") 

        if not telegram_chatid:
            print("Warning: Telegram chat id not specified")

    telegram = telegram_enabled and telegram_token and telegram_chatid

    read_function = read_sensor_data if is_pi else generate_sensor_data
    def read_sensors():
        with app.app_context():
            humidity, temperature = read_function()
            if not humidity or not temperature:
                print("Warning: failed to read humidity and temperature")
                return
            d = db.get_db()
            d.execute(
                'INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)',
                (int(temperature), int(humidity))
            )
            d.commit()

            if telegram and humidity < threshold:
                send_telegram_msg(humidity)

    def send_telegram_msg(humidity):
        payload = {'chat_id': telegram_chatid,
                'text': 'Humidity is currently {}%, which is below the threshold of < {}%'.format(humidity, threshold)}
        requests.post('https://api.telegram.org/bot{}/sendMessage'.format(telegram_token), data = payload)

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(read_sensors, 'interval', seconds=polling_interval)
    sched.start()

    print("Started with polling interval {} seconds and telegram {}".format(polling_interval, "enabled" if telegram else "disabled"))

    return app

#if __name__ == '__main__':
#    create_app().run(debug = False, host = '0.0.0.0')
