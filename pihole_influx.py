#! /usr/bin/python

# Script originally created by JON HAYWARD: https://fattylewis.com/Graphing-pi-hole-stats/
# Adapted to work with InfluxDB by /u/tollsjo in December 2016
# Updated by Cludch December 2016
# Updated and dockerised by rarosalion in September 2019

# To install and run the script as a service under SystemD. See: https://linuxconfig.org/how-to-automatically-execute-shell-script-at-startup-boot-on-systemd-linux

import requests
import time
import json
import os
import logging
from influxdb import InfluxDBClient

# Modify these values if running as a standalone script
_DEFAULTS = {
    'INFLUXDB_SERVER': "127.0.0.1",  # IP or hostname to InfluxDB server
    'INFLUXDB_PORT': 8086,  # Port on InfluxDB server
    'INFLUXDB_USERNAME': "username",
    'INFLUXDB_PASSWORD': "password",
    'INFLUXDB_DATABASE': "piholestats",
    'DELAY': 600,  # seconds
    'PIHOLE_HOSTS': ["pi.hole"]  # Pi-hole hostname(s)
}


def get_config():
    """ Combines config options from config.json file and environment variables """

    # Read a config file (json dictionary) if it exists in the script folder
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(script_dir, 'config.json')
    if os.path.exists(config_file):
        config = json.load(open(config_file))
    else:
        config = _DEFAULTS

    # Overwrite config with environment variables (set via Docker)
    for var_name in _DEFAULTS.keys():
        config[var_name] = os.getenv(var_name, _DEFAULTS[var_name])
        if var_name == 'PIHOLE_HOSTS' and ',' in config[var_name]:
            config[var_name] = config[var_name].split(',')

    # Make sure PIHOLE_HOSTS is a list (even if it's just one entry)
    if not isinstance(config['PIHOLE_HOSTS'], list):
        config['PIHOLE_HOSTS'] = [config['PIHOLE_HOSTS']]

    return config


def check_db_status(config, logger):
    """ Check the required DB exists, and create it if necessary """

    logger.debug("Connecting to {}".format(config['INFLUXDB_SERVER']))
    client = InfluxDBClient(
        config['INFLUXDB_SERVER'],
        config['INFLUXDB_PORT'],
        config['INFLUXDB_USERNAME'],
        config['INFLUXDB_PASSWORD']
    )
    for db in client.get_list_database():
        if db['name'] == client:
            logger.info('Found existing database {}.'.format(config['INFLUXDB_DATABASE']))
            return True
    else:
        logger.info('Database {} not found. Will attempt to create it.'.format(config['INFLUXDB_DATABASE']))
        client.create_database(config['INFLUXDB_DATABASE'])
    return True


def send_msg(config, logger, hostname, domains_being_blocked, dns_queries_today, ads_percentage_today, ads_blocked_today):
    """ Sends message to InfluxDB server defined in config """
    json_body = [
        {
            "measurement": "piholestats." + hostname.replace(".", "_"),
            "tags": {
                "host": hostname
            },
            "fields": {
                "domains_being_blocked": int(domains_being_blocked),
                "dns_queries_today": int(dns_queries_today),
                "ads_percentage_today": float(ads_percentage_today),
                "ads_blocked_today": int(ads_blocked_today)
            }
        }
    ]
    logger.debug(json_body)

    # InfluxDB host, InfluxDB port, Username, Password, database
    client = InfluxDBClient(
        config['INFLUXDB_SERVER'],
        config['INFLUXDB_PORT'],
        config['INFLUXDB_USERNAME'],
        config['INFLUXDB_PASSWORD'],
        config['INFLUXDB_DATABASE']
    )

    client.write_points(json_body)
    print(json_body)


if __name__ == '__main__':

    # Setup logger
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

    # Get configuration details
    config = get_config()
    logger.info("Querying {} pihole servers: {}".format(len(config['PIHOLE_HOSTS']), config['PIHOLE_HOSTS']))
    logger.info("Logging to InfluxDB server {}:{}".format(
        config['INFLUXDB_SERVER'], config['INFLUXDB_PORT']
    ))

    # Create database if it doesn't exist
    check_db_status(config, logger)

    # Loop pulling stats from pihole, and pushing to influxdb
    while True:
        for host in config['PIHOLE_HOSTS']:

            # Get PiHole Stats
            pihole_api = "{}/admin/api.php".format(host)
            logger.info("Attempting to contact {} with URL {}".format(host, pihole_api))
            api = requests.get(pihole_api)  # URI to pihole server api
            API_out = api.json()
            domains_being_blocked = (API_out['domains_being_blocked'])
            dns_queries_today = (API_out['dns_queries_today'])
            ads_percentage_today = (API_out['ads_percentage_today'])
            ads_blocked_today = (API_out['ads_blocked_today'])

            # Update DB
            send_msg(config, logger, host, domains_being_blocked, dns_queries_today, ads_percentage_today, ads_blocked_today)

        # Wait...
        logger.info("Waiting {}".format(config['DELAY']))
        time.sleep(int(config['DELAY']))
