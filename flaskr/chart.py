from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
from flaskr.db import get_db

from datetime import datetime
from itertools import groupby, chain

bp = Blueprint("chart", __name__)

@bp.route("/")
def index():
	def extract_day(dt):
		return dt.day

	db = get_db()
	qry = 'SELECT * FROM (SELECT created, humidity, temperature FROM sensor_data ORDER BY created ASC limit 72) ORDER BY created ASC'
	sensor_data = db.execute(qry).fetchall()

	dates = [row['created'] for row in sensor_data]
	grouped_dates = [ (day, list(values)) for day, values in groupby(dates, extract_day) ]
	date_labels = [assign_time_label(list(values)) for day, values in grouped_dates]

	date_labels = list(chain(*date_labels))
	humidities = [row['humidity'] for row in sensor_data]
	temperatures = [row['temperature'] for row in sensor_data]

	return render_template('index.html', dates = date_labels, humidities = humidities, temperatures = temperatures, threshold = app.config['THRESHOLD'])


def assign_time_label(r):
	for index, item in enumerate(r):
		yield item.strftime('%H:%M') if index > 0 else item.strftime('%d-%m-%Y %H:%M')