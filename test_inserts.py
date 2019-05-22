#!/usr/bin/python3
from random import randint

if __name__ == "__main__":
	q = "INSERT INTO sensor_data('created', 'humidity', 'temperature') VALUES (datetime(CURRENT_TIMESTAMP, '{} minutes'), '{}', '{}');"

	for m in range(-172800, 200, +30):
		print(q.format("{}{}".format("+" if m >= 0 else "", m), randint(0, 80), randint(0, 40)))
