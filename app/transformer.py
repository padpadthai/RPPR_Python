import datetime
import logging
import re
import string
from decimal import Decimal

from app.property_price_register import RawPropertySale


def transform_date(date: str) -> datetime:
    return datetime.datetime.strptime(date, "%d/%m/%Y").date()


def transform_size_description(size_description: str) -> str:
    if size_description == "less than 38 sq metres":
        return "small"
    elif size_description == "greater than or equal to 38 sq metres and less than 125 sq metres":
        return "medium"
    elif size_description == "greater than or equal to 125 sq metres":
        return "large"
    else:
        # todo: maybe change this to None but need to run regression on db read/write
        return ""


price_regex = re.compile(r'[€,]')


def transform_price(price: str) -> Decimal:
    clean_price = price_regex.sub('', price)
    return Decimal(clean_price)


# all should be not be surrounded by more words
address_abbreviations = {
    re.compile(r"\s+Apts\s+"): "Apartments",
    re.compile(r"\s+Ave\s+"): "Avenue",
    re.compile(r"\s+Ave\s+"): "Avenue",
    re.compile(r"\s+Blvd\s+"): "Boulevard",
    re.compile(r"\s+Bldg\s+"): "Building",
    re.compile(r"\s+Ct\s+"): "Court",
    re.compile(r"\s+Cts\s+"): "Courts",
    re.compile(r"\s+Cres\s+"): "Crescent",
    re.compile(r"\s+Dr\s+"): "Drive",
    re.compile(r"\s+Est\s+"): "Estate",
    re.compile(r"\s+Ft\s+"): "Fort",
    re.compile(r"\s+Frnt\s+"): "Front",
    re.compile(r"\s+Gdn\s+"): "Garden",
    re.compile(r"\s+Gdns\s+"): "Gardens",
    re.compile(r"\s+Gln\s+"): "Glen",
    re.compile(r"\s+Grv\s+"): "Grove",
    re.compile(r"\s+Grvs\s+"): "Groves",
    re.compile(r"\s+Hvn\s+"): "Haven",
    re.compile(r"\s+Hts\s+"): "Heights",
    re.compile(r"\s+Hl\s+"): "Hill",
    re.compile(r"\s+Hls\s+"): "Hills",
    re.compile(r"\s+Hse\s+"): "House",
    re.compile(r"\s+Isl\s+"): "Island",
    re.compile(r"\s+Ln\s+"): "Lane",
    re.compile(r"\s+Ldg\s+"): "Lodge",
    re.compile(r"\s+Lwr\s+"): "Lower",
    re.compile(r"\s+Mnr\s+"): "Manor",
    re.compile(r"\s+Mdw\s+"): "Meadow",
    re.compile(r"\s+Mdws\s+"): "Meadows",
    re.compile(r"\s+Mls\s+"): "Mills",
    re.compile(r"\s+Mt\s+"): "Mount",
    re.compile(r"\s+Orch\s+"): "Orchard",
    re.compile(r"\s+Pk\s+"): "Park",
    re.compile(r"\s+Pl\s+"): "Place",
    re.compile(r"\s+Plz\s+"): "Plaza",
    re.compile(r"\s+Pt\s+"): "Point",
    re.compile(r"\s+Riv\s+"): "River",
    re.compile(r"\s+Rd\s+"): "Road",
    re.compile(r"\s+Sq\s+"): "Square",
    re.compile(r"\s+Spr\s+"): "Spring",
    re.compile(r"\s+Spg\s+"): "Spring",
    re.compile(r"\s+Spgs\s+"): "Springs",
    re.compile(r"\s+Sta\s+"): "Station",
    re.compile(r"(?<!\d)\s+St\s+"): "Street",  # not first or after number, more than likely saint
    re.compile(r"\s+Ter\s+"): "Terrace",
    re.compile(r"\s+Uppr\s+"): "Upper",
    re.compile(r"\s+Vw\s+"): "View",
    re.compile(r"\s+Vlg\s+"): "Village"
}

start_regex = re.compile(r'^\s*(Apts?|Apartments?|Flts?|Flats?|Nos?|Nums?|Numbers?|Houses?)', flags=re.IGNORECASE)
non_valid_regex = re.compile(r'([^\s\d\w])')
county_regex = re.compile(r'Co(?<=\w)(?!\w)', flags=re.IGNORECASE)
multiples_regex = re.compile(r'^(\d+(\w{1})?(\s*And)?\W+){2,}', flags=re.IGNORECASE)


def transform_address(address: str, postcode: str, county: str) -> str:
    new_address = address
    if non_valid_regex.search(new_address):
        new_address = non_valid_regex.sub(' ', new_address)
    new_address = new_address.lstrip()
    if start_regex.match(new_address):
        new_address = start_regex.sub(' ', new_address)
    if county_regex.search(new_address):
        new_address = county_regex.sub(' ', new_address)
    new_address = new_address.lstrip()
    if multiples_regex.match(new_address):
        new_address = multiples_regex.sub(' ', new_address)
    new_address = string.capwords(new_address)  # captialise each word and clean whitespace
    if postcode not in new_address:
        new_address += " " + postcode  # add post code
    if county not in new_address:
        new_address += " " + county  # add county
    for key, value in address_abbreviations.items():  # replace abbreviations
        if key.search(new_address):
            new_address = re.sub(key, " " + value + " ", new_address)
    # logging.debug("'{}' -> '{}'".format(address, new_address))
    return new_address


class TransformedPropertySale:

    def __init__(self, app_id: str, date: datetime, address: str, postcode: str, county: str, price: Decimal,
                 full_price: bool, vat_exclusive: bool, new: bool, size: str):
        self.app_id = app_id
        self.date: datetime = date
        self.address: str = address
        self.postcode: str = postcode
        self.county: str = county
        self.price: Decimal = price
        self.full_price: bool = full_price
        self.vat_exclusive: bool = vat_exclusive
        self.new: bool = new
        self.size: str = size

    def json_serialise(self):
        fields = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                fields[key] = value.isoformat()
            elif isinstance(value, Decimal):
                fields[key] = str(value)  # this could result in a loss of precision
            else:
                fields[key] = value
        return fields

    def __str__(self):
        return "{} - {} - {} - {}".format(self.app_id, self.date, self.address, self.price)


def transformed_from_raw(raw_property_sale: RawPropertySale) -> TransformedPropertySale:
    return TransformedPropertySale(raw_property_sale.app_id, transform_date(raw_property_sale.date),
               transform_address(raw_property_sale.address, raw_property_sale.postcode, raw_property_sale.county),
               raw_property_sale.postcode, raw_property_sale.county, transform_price(raw_property_sale.price),
               raw_property_sale.not_full_price == "No", raw_property_sale.vat_exclusive == "Yes",
               raw_property_sale.property_description == "New Dwelling house /Apartment",
               transform_size_description(raw_property_sale.size_description))
