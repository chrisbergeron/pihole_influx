## Pihole_Influx

A couple of basic scripts for inserting pihole data into influxdb for graphing.

*pihole_influx.py* - A python script for inserting records into influxdb.

Configuration options:
``` bash
HOSTNAMES = "ns-01" # Pi-hole hostname(s) to report in InfluxDB for each measurement. Comma separated list.
INFLUXDB_SERVER = "127.0.0.1" # IP or hostname to InfluxDB server
INFLUXDB_PORT = 8086 # Port on InfluxDB server
INFLUXDB_USERNAME = "username"
INFLUXDB_PASSWORD = "password"
INFLUXDB_DATABASE = "piholestats"
DELAY = 600 # seconds
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

---

If your **Docker build fails on a 32-bit ARM host** (e.g. Raspberry Pi on Raspbian Buster) with:
```
Fatal Python error: _Py_InitializeMainInterpreter: can't initialize time
PermissionError: [Errno 1] Operation not permitted
```
this is the well-known `libseccomp2` / `time64` syscall problem. Newer Alpine base
images (3.13+) use musl 1.2, which issues 64-bit-time syscalls that an old
`libseccomp2` (< 2.4.4) blocks under Docker's default seccomp profile. Two fixes:

1. **Update the host (recommended, fixes it for all containers):**
   ```bash
   echo 'deb http://httpredir.debian.org/debian buster-backports main contrib non-free' | \
     sudo tee /etc/apt/sources.list.d/buster-backports.list
   sudo apt-get update
   sudo apt-get -t buster-backports install libseccomp2
   ```
2. **No host change:** this repo's `Dockerfile` is pinned to `python:3.7-alpine3.12`
   (musl 1.1.x, no time64 syscalls), so `docker-compose build` works as-is.
