from typing import Tuple

from geopy import Location, Nominatim as Nominatim_geopy

from app import config
from app.geocoding.provider import Provider

internal_config = config['geocoders']['nominatim']


class Nominatim(Provider):

    def __init__(self):
        self.geocoder = Nominatim_geopy(domain=internal_config['domain'], scheme=internal_config['scheme'])

    def raw_location_keys(self) -> Tuple:
        return 'boundingbox', 'class', 'importance', 'osm_id', 'osm_type', 'place_id', 'type'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'nominatim'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address, country_codes=["ie"])

