import logging
import sys
from pathlib import Path

import psycopg2
import yaml

with open("resources/config.yaml") as yaml_config:
    config = yaml.safe_load(yaml_config)

with open("resources/secrets.yaml") as yaml_config:
    secrets = yaml.safe_load(yaml_config)

logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.getLevelName(config['logging']['level']))

logging.getLogger('urllib3').setLevel(logging.WARN)

def __finditem(obj, key):
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = __finditem(v, key)
            if item is not None:
                paths.append(item)


paths = []


def init_paths(conf, path_key):
    __finditem(conf, path_key)
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


init_paths(config, 'path')


def get_connection():
    try:
        return psycopg2.connect(config['postgres']['connection'])
    except psycopg2.Error:
        logging.error("There was a problem connecting to the PostgreSQL database")
        raise
