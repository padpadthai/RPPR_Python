import json
import logging
from datetime import datetime
from typing import List

import geopy
import pymongo
# from bson.json_util import dumps
from bson import json_util
from geopy import Location
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
from pymongo import InsertOne, UpdateOne

from app import config
from app.geocoding.provider import Provider

logging.getLogger('geopy').setLevel(logging.WARN)

client = pymongo.MongoClient(config['mongo']['connection'])
database = client.get_database(config['geocoding']['database'])
collection = database.get_collection(config['geocoding']['store'])
collection.create_index("address")

geopy.geocoders.options.default_timeout = config['geocoding']['timeout']


def update_addresses(addresses: List[str]):
    logging.debug("Updating address collection '{}'".format(collection.name))
    existing_addresses = set(cursor['address'] for cursor in collection.find())
    different_addresses = [x for x in addresses if x not in existing_addresses]
    logging.debug("Inserting '{}' new addresses into '{}'".format(len(different_addresses), collection.name))
    operations = [InsertOne({"address": address, 'geocoded': {}}) for address in different_addresses]
    if len(operations) > 0:
        collection.bulk_write(operations)
        logging.info("Inserted addresses into collection '{}'".format(collection.name))


def __process_location(location: Location, address: str, provider: Provider, processed_key: str, time: datetime) -> UpdateOne:
    if location is not None:
        data = {key: location.raw.get(key, None) for key in provider.raw_location_keys()}
        return UpdateOne({"address": address},
                     {"$set": {"geocoded." + provider.identifier():
                         {
                             "address": location.address,
                             "altitude": location.altitude,
                             "latitude": location.latitude,
                             "longitude": location.longitude,
                             "raw": data
                         },
                         "geocoded." + processed_key: time
                     }
                     })
    else:
        return UpdateOne({"address": address}, {"$set": {"geocoded." + processed_key: time}})


def __bulk_write(operations, provider_identifier):
    logging.debug("Writing '{}' from '{}' geocodings to '{}'".format(len(operations), provider_identifier, collection.name))
    collection.bulk_write(operations)


def geocode(provider: Provider):
    processed_key = provider.identifier() + config['geocoding']['processed-suffix']
    flush_count = config['geocoding']['flush-count']
    unprocessed_addresses = collection.find({"geocoded." + processed_key: None})
    operations = list()
    count = 0
    time = datetime.now()
    logging.info("'{}' addresses to geocode with '{}'".format(unprocessed_addresses.count(), provider.identifier()))
    for unprocessed_address in unprocessed_addresses:
        address = unprocessed_address['address']
        try:
            location: Location = provider.geocode(address)
            operations.append(__process_location(location, address, provider, processed_key, time))
            count += 1
        except GeocoderTimedOut:
            logging.warning("Geocoder timed out on address '{}'".format(address))
        except GeocoderQuotaExceeded:
            logging.warning("Geocoder quota exceeded with '{}'".format(provider.identifier()))
            break
        if count % flush_count == 0 and count != 0 and len(operations) != 0:
            __bulk_write(operations, provider.identifier())
            operations.clear()
        if count >= provider.max_requests() != -1:
            break
    if len(operations) != 0:
        __bulk_write(operations, provider.identifier())


def export_collection(output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(list(collection.find()), file, default=json_util.default, ensure_ascii=False, indent=4)
        logging.info("Exported transformed sales to '{}'".format(output_file))
    except IOError:
        logging.error("Unable to process file '{}'".format(output_file))
        raise ValueError("There was an issue writing to the file '{}'".format(output_file))
