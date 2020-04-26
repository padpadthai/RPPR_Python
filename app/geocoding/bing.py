
from typing import Tuple

from geopy import Bing as Bing_geopy, Point, Location

from app import config, secrets
from app.geocoding.provider import Provider

internal_config = config['geocoders']['bing']


class Bing(Provider):

    def __init__(self):
        self.geocoder = Bing_geopy(api_key=secrets['api-key']['bing'])

    def raw_location_keys(self) -> Tuple:
        return 'bbox', 'address', 'confidence', 'entityType', 'geocodePoints', 'matchCodes'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'bing'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address, user_location=Point(longitude=-8, latitude=53.5))
