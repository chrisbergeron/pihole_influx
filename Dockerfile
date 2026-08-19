# Pin to alpine3.12 (musl 1.1.x). Newer Alpine (3.13+) ships musl 1.2 which uses
# 64-bit time (time64) syscalls. On 32-bit ARM hosts (e.g. Raspbian Buster on a
# Raspberry Pi) with an old libseccomp2 (< 2.4.4), Docker's default seccomp
# profile blocks those syscalls, so pip/python dies at build time with:
#   Fatal Python error: _Py_InitializeMainInterpreter: can't initialize time
#   PermissionError: [Errno 1] Operation not permitted
# Pinning avoids it with no host changes. Alternatively update the host:
#   sudo apt-get -t buster-backports install libseccomp2   (see README).
FROM python:3.7-alpine3.12

RUN pip install --no-cache-dir influxdb

WORKDIR /usr/src/app

COPY pihole_influx.py ./

CMD [ "python", "/usr/src/app/pihole_influx.py" ]