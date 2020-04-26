import logging
from typing import List

from app import config, get_connection
from app.property_price_register import RawPropertySale
from app.transformer import TransformedPropertySale
from app.util import postgres


def persist_raw_sales(property_sales: List[RawPropertySale]):
    table_name = config['storage']['table']['raw']
    postgres.drop_table(get_connection(), table_name)
    logging.debug("Dropped table '{}'".format(table_name))
    __create_raw_sale_table(table_name)
    logging.debug("Table '{}' is available".format(table_name))
    __insert_raw_property_sales(table_name, property_sales)


def read_raw_sales() -> List[RawPropertySale]:
    table_name = config['storage']['table']['raw']
    logging.debug("Reading all raw property sales from '{}'".format(table_name))
    sales = postgres.read_all(get_connection(), table_name)
    return [__create_raw_sale_from_db(db_tuple) for db_tuple in sales]


def __create_raw_sale_from_db(db_tuple) -> RawPropertySale:
    instance = RawPropertySale(db_tuple[2], db_tuple[3], db_tuple[4], db_tuple[5], db_tuple[6], db_tuple[7],
                               db_tuple[8], db_tuple[9], db_tuple[10])
    instance.app_id = db_tuple[1]
    return instance


def __create_raw_sale_table(table_name: str):
    postgres.create_table(get_connection(), table_name,
                          ["id serial PRIMARY KEY",
                           "app_id varchar(36) NOT NULL UNIQUE",
                           "date varchar(20)",
                           "address varchar(255)",
                           "postcode varchar(20)",
                           "county varchar(20)",
                           "price varchar(20)",
                           "not_full_price varchar (20)",
                           "vat_exclusive varchar (20)",
                           "property_description varchar(255)",
                           "size_description varchar(255)"
                           ])


def __insert_raw_property_sales(table_name: str, property_sales: List[RawPropertySale]):
    postgres.bulk_insert(get_connection(), table_name,
                         ["app_id", "date", "address", "postcode", "county", "price", "not_full_price", "vat_exclusive",
                          "property_description", "size_description"],
                         ((sale.app_id, sale.date, sale.address, sale.postcode, sale.county, sale.price,
                           sale.not_full_price, sale.vat_exclusive, sale.property_description, sale.size_description)
                          for sale in property_sales))


def persist_transformed_sales(transformed_sales: List[TransformedPropertySale]):
    table_name = config['storage']['table']['transformed']
    postgres.drop_table(get_connection(), table_name)
    logging.debug("Dropped table '{}'".format(table_name))
    __create_transformed_sales_table(table_name)
    logging.debug("Table '{}' is available".format(table_name))
    __insert_transformed_sales(table_name, transformed_sales)


def read_transformed_sales() -> List[TransformedPropertySale]:
    table_name = config['storage']['table']['transformed']
    logging.debug("Reading all transformed property sales from '{}'".format(table_name))
    sales = postgres.read_all(get_connection(), table_name)
    return [__create_transformed_sale_from_db(db_tuple) for db_tuple in sales]


def __create_transformed_sale_from_db(db_tuple) -> TransformedPropertySale:
    return TransformedPropertySale(db_tuple[1], db_tuple[2], db_tuple[3], db_tuple[4], db_tuple[5], db_tuple[6],
                                   db_tuple[7], db_tuple[8], db_tuple[9], db_tuple[10])


def __create_transformed_sales_table(table_name: str):
    postgres.create_table(get_connection(), table_name,
                          ["id serial PRIMARY KEY",
                           "app_id varchar(36) NOT NULL UNIQUE",
                           "date date",
                           "address varchar(255)",
                           "postcode varchar(20)",
                           "county varchar(20)",
                           "price decimal",
                           "full_price boolean",
                           "vat_exclusive boolean",
                           "new boolean",
                           "size varchar(20)"
                           ])


def __insert_transformed_sales(table_name: str, property_sales: List[TransformedPropertySale]):
    postgres.bulk_insert(get_connection(), table_name,
                         ["app_id", "date", "address", "postcode", "county", "price", "full_price", "vat_exclusive",
                          "new", "size"],
                         ((sale.app_id, sale.date, sale.address, sale.postcode, sale.county, sale.price,
                           sale.full_price, sale.vat_exclusive, sale.new, sale.size)
                          for sale in property_sales))
