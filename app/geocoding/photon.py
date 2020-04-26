from typing import Tuple

from geopy import Location, Photon as Photon_geopy, Point

from app import config
from app.geocoding.provider import Provider

internal_config = config['geocoders']['photon']


class Photon(Provider):

    def __init__(self):
        self.geocoder = Photon_geopy()

    def raw_location_keys(self) -> Tuple:
        return 'geometry', 'properties', 'type'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'photon'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address, location_bias=Point(longitude=-8, latitude=53.5))