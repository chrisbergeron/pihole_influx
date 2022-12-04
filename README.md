## Pihole_Influx

A couple of basic scripts for inserting pihole data into influxdb for graphing.

*pihole_influx.py* - A python script for inserting records into influxdb.

Configuration options:
``` bash
INFLUXDB_SERVER = "127.0.0.1" # IP or hostname to InfluxDB server
INFLUXDB_PORT = 8086 # Port on InfluxDB server
INFLUXDB_USERNAME = "username"
INFLUXDB_PASSWORD = "password"
INFLUXDB_DATABASE = "piholestats"
DELAY = 600 # seconds
PIHOLE_HOSTS = "ns-01" # Pi-hole hostname(s) to report in InfluxDB for each measurement. Comma separated list.
PIHOLE_TOKENS = "token1" # Pi-hole token(s) to use to connect to the API. Comma separated list. Token can be captured from value WEBPASSWORD in setupVars.conf in /etc/pihole.
```
*docker-compose.yml* - An example Docker setup to run this script

Configuration options above can be specified within the environment section of the compose file.

*pihole-influx.service* - A SystemD Unit File for starting pihole_influx at boot (and logging)
On Centos7, put this file in /lib/systemd/system/.

Run:
``` bash
systemctl daemon-reload
systemctl enable pihole-influx
systemctl start pihole-influx
```

To run pihole_influx.py from the command line without the startup script:
```bash
/usr/bin/python ./pihole_influx.py
```

I installed this script in /opt/pihole_influx.  If you put it somewhere else you'll have to update the systemD startup script.

NOTE: The script pauses for DELAY seconds at start because I had problems with the systemD script if it was started to early.  If you know how to fix this please submit a pull request.

### Troubleshooting
If you get the following error:
```
Traceback (most recent call last): File "./pihole_influx.py", line 11, in <module> from influxdb import InfluxDBClient
```
You'll need to install the python-influxdb module for python.  On a raspberry pi, you can do this with:
```
sudo apt-get install python-influxdb
```

Or on CentOS / RHEL:
```
yum install python-influxdb
```
---

If you get this error:
```
Traceback (most recent call last): File "./pihole_influx.py", line 8, in <module> import requests ImportError: No module named requests
```
You'll need to install the python-requests module.
