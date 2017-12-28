## Pihole_Influx

A couple of basic scripts for inserting pihole data into influxdb for graphing.

pihole_influx.py - A python script for inserting records into influxdb.

Configuration options:
HOSTNAME = "ns-01" # Pi-hole hostname to report in InfluxDB for each measurement
PIHOLE_API = "http://PI_HOLE_IP_ADDRESS_HERE/admin/api.php"
INFLUXDB_SERVER = "127.0.0.1" # IP or hostname to InfluxDB server
INFLUXDB_PORT = 8086 # Port on InfluxDB server
INFLUXDB_USERNAME = "username"
INFLUXDB_PASSWORD = "password"
INFLUXDB_DATABASE = "piholestats"
DELAY = 600 # seconds

pihole-influx.service - A SystemD Unit File for starting pihole_influx at boot (and logging)
