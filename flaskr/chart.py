from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
from flaskr.db import get_db

from datetime import datetime

bp = Blueprint("chart", __name__)

@bp.route("/")
def index():
	db = get_db()
	qry = 'SELECT created, humidity, temperature FROM sensor_data ORDER BY created ASC limit 144'
	sensor_data = db.execute(qry).fetchall()

	created = [row['created'].strftime('%H:%M') for row in sensor_data]
	humidities = [row['humidity'] for row in sensor_data]
	temperatures = [row['temperature'] for row in sensor_data]

	return render_template('index.html', dates = created, humidities = humidities, temperatures = temperatures, threshold = app.config['THRESHOLD'])