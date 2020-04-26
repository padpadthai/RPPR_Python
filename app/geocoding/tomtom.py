from typing import Tuple

from geopy import Location, TomTom as TomTom_geopy

from app import config, secrets
from app.geocoding.provider import Provider

internal_config = config['geocoders']['tomtom']


class TomTom(Provider):

    def __init__(self):
        self.geocoder = TomTom_geopy(api_key=secrets['api-key']['tomtom'])

    def raw_location_keys(self) -> Tuple:
        return 'score', 'address', 'position', 'viewport'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'tomtom'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address)

