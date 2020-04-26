import json
import logging
from typing import List

import app.analyser as analysis
import app.geocoder as geocoding
import app.property_price_register as price_register
import app.sanitiser as sanitiser
import app.transformer as transformer
from app import config, storage
from app.geocoding.arcgis import ArcGIS
from app.geocoding.azure import Azure
from app.geocoding.bing import Bing
from app.geocoding.google import Google
from app.geocoding.here import Here
from app.geocoding.mapbox import MapBox
from app.geocoding.nominatim import Nominatim
from app.geocoding.opencage import OpenCage
from app.geocoding.photon import Photon
from app.geocoding.tomtom import TomTom
from app.property_price_register import RawPropertySale
from app.transformer import TransformedPropertySale


def get_raw_sales() -> List[RawPropertySale]:
    if config['register']['download']['enabled']:
        price_register.download_csv()
        logging.info("Downloaded and extracted raw property sales csv file")
    raw_sales = price_register.parse_csv()
    logging.info("'{}' raw property sales prices received".format(len(raw_sales)))
    if config['register']['persist']['enabled']:
        storage.persist_raw_sales(raw_sales)
        logging.info("Persisted raw property sales")
    return raw_sales


def clean_sales(sales=None) -> List[TransformedPropertySale]:
    if sales is None:
        sales = storage.read_raw_sales()
    logging.info("Received '{}' raw sales".format(len(sales)))
    # it could be nice to deep copy of raw property sales but didn't for efficiency and memory concerns
    if config['data_clean']['sanitiser']['enabled']:
        sales = [sanitiser.Sanitiser(sale).sanitise() for sale in sales]
        logging.info("Sanitised raw property sales")
    logging.info("Transforming property sales")
    sales = [transformer.transformed_from_raw(sale) for sale in sales]
    logging.info("Transformed property sales")
    if config['data_clean']['persist']['enabled']:
        storage.persist_transformed_sales(sales)
        logging.info("Persisted transformed sales")
    if config['data_clean']['output']['enabled']:
        output_file = config['data_clean']['output']['path'] + "sales.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump([sale.json_serialise() for sale in sales], file, ensure_ascii=False, indent=4)
            logging.info("Exported transformed sales to '{}'".format(output_file))
        except IOError:
            logging.error("Unable to process file '{}'".format(output_file))
            raise ValueError("There was an issue writing to the file '{}'".format(output_file))
    return sales


def analyse_data(sales=None):
    if sales is None:
        sales = storage.read_transformed_sales()
    logging.info("Received '{}' transformed sales".format(len(sales)))
    analyser = analysis.Analyser(sales)
    if config['analysis']['totals']['enabled']:
        analyser.log_totals()
    if config['analysis']['output']['transformed']['enabled']:
        analysis_data_file = config['analysis']['output']['transformed']['path'] + "analysis_data.csv"
        logging.info("Writing transformed data for analysis to '{}'".format(analysis_data_file))
        analyser.data_frame.to_csv(analysis_data_file)
    descriptives = analyser.get_descriptives()
    if config['analysis']['output']['descriptives']['enabled']:
        descriptives_output_path = config['analysis']['output']['descriptives']['path']
        logging.info(
            "Writing descriptive statistics for various data aggregations to '{}'".format(descriptives_output_path))
        for descriptive in descriptives:
            descriptive['data'].to_csv(descriptives_output_path + descriptive['name'] + ".csv")
    analyser.time_analysis()
    analyser.new_old_analysis()
    if config['analysis']['plots']['output']['enabled']:
        logging.info("Exporting interactive HTML plots to '{}'".format(config['analysis']['plots']['output']['path']))
        analyser.output_plots()
    if config['analysis']['plots']['show']['enabled']:
        logging.info("Displaying the plots on a local browser")
        analyser.show_plots()
    if config['analysis']['plots']['upload']['enabled']:
        logging.info("Uploading plots to Chart Studio")
        analyser.upload_plots_to_chart_studio()


geocoders = [
    {'config_key': 'nominatim', 'implementation': Nominatim()},
    {'config_key': 'bing', 'implementation': Bing()},
    {'config_key': 'arcgis', 'implementation': ArcGIS()},
    {'config_key': 'here', 'implementation': Here()},
    {'config_key': 'photon', 'implementation': Photon()},
    {'config_key': 'azure', 'implementation': Azure()},
    {'config_key': 'mapbox', 'implementation': MapBox()},
    {'config_key': 'opencage', 'implementation': OpenCage()},
    {'config_key': 'tomtom', 'implementation': TomTom()},
    {'config_key': 'google', 'implementation': Google()},
]


def geocode(sales=None):
    if sales is None:
        sales = storage.read_transformed_sales()
    logging.info("Received '{}' sales".format(len(sales)))
    geocoding.update_addresses([sale.address for sale in sales])
    for geocoder in geocoders:
        if config['geocoders'][geocoder['config_key']]['enabled']:
            geocoding.geocode(geocoder['implementation'])
    if config['geocoding']['export']['enabled']:
        output_file = config['geocoding']['export']['path'] + "geocoding.json"
        geocoding.export_collection(output_file)


if config['pipeline']['enabled']['get-raw-data']:
    raw_property_sales = get_raw_sales()
if config['pipeline']['enabled']['clean-data']:
    transformed_property_sales = clean_sales()
if config['pipeline']['enabled']['analyse']:
    analyse_data()
if config['pipeline']['enabled']['geocode']:
    geocode()
