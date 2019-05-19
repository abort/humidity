DROP TABLE IF EXISTS sensor_data;

CREATE TABLE sensor_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  temperature INTEGER NOT NULL,
  humidity INTEGER NOT NULL
);

INSERT INTO sensor_data(created, temperature, humidity) values(datetime(1558285864, 'unixepoch'), 17, 30);
INSERT INTO sensor_data(created, temperature, humidity) values(datetime(1558287664, 'unixepoch'), 20, 40);
INSERT INTO sensor_data(created, temperature, humidity) values(datetime(1558289464, 'unixepoch'), 10, 60);
INSERT INTO sensor_data(created, temperature, humidity) values(datetime(1558291264, 'unixepoch'), 20, 40);