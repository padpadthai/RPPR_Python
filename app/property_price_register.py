import csv
import logging
import os
import sys
from typing import List
from uuid import uuid4

from app import config
from app.util import remote

output_file = config['register']['csv']['output']['path'] + config['register']['csv']['output']['file']


class RawPropertySale:

    def __init__(self, date: str, address: str, postcode: str, county: str, price: str,
                 not_full_price: str, vat_exclusive: str, property_description: str, size_description: str):
        self.app_id: str = str(uuid4())
        self.date: str = date
        self.address: str = address
        self.postcode: str = postcode
        self.county: str = county
        self.price: str = price
        self.not_full_price: str = not_full_price
        self.vat_exclusive: str = vat_exclusive
        self.property_description: str = property_description
        self.size_description: str = size_description

    def __str__(self):
        return "{} - {} - {} - {}".format(self.app_id, self.date, self.address, self.price)


def download_csv():
    extracted_files = remote.extract_remote_zip(
        config['register']['download']['url'],
        config['register']['csv']['output']['path'],
        ssl_verify=False)
    if len(extracted_files) != 1:
        logging.error("Must be only one .csv file to process")
        sys.exit(1)
    os.rename(extracted_files[0], output_file)
    logging.debug("Downloaded property price register csv to file '{}'".format(output_file))


def parse_csv() -> List[RawPropertySale]:
    logging.debug("Reading property price register data from file '{}'".format(output_file))
    property_sales = list()
    try:
        with open(output_file, 'r', encoding="cp1252") as property_price_file:  # Windows encoding
                reader = csv.reader(property_price_file)
                next(reader)  # skip header row with column descriptions
                for row in reader:
                    property_sales.append(RawPropertySale(row[0], row[1], row[2], row[3], row[4],
                                                          row[5], row[6], row[7], row[8]))
    except IOError:
        logging.error("Unable to process file '{}'".format(output_file))
        raise ValueError("There was an issue reading from the file '{}'".format(output_file))
    logging.debug("Consumed property price register data from file '{}'".format(output_file))
    return property_sales  # this is quite a big list so memory limits could be an issue
