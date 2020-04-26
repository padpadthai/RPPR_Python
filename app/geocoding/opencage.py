from typing import Tuple

from geopy import Location, OpenCage as OpenCage_geopy

from app import config, secrets
from app.geocoding.provider import Provider

internal_config = config['geocoders']['opencage']


class OpenCage(Provider):

    def __init__(self):
        self.geocoder = OpenCage_geopy(api_key=secrets['api-key']['opencage'])

    def raw_location_keys(self) -> Tuple:
        return 'bounds', 'components', 'confidence', 'formatted', 'geometry'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'opencage'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address, country="ie")

