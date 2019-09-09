FROM python:3.7-alpine

RUN pip install --no-cache-dir influxdb

WORKDIR /usr/src/app

COPY pihole_influx.py ./

CMD [ "python", "/usr/src/app/pihole_influx.py" ]