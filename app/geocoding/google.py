from typing import Tuple

from geopy import Location, GoogleV3

from app import config, secrets
from app.geocoding.provider import Provider

internal_config = config['geocoders']['google']


class Google(Provider):

    def __init__(self):
        self.geocoder = GoogleV3(api_key=secrets['api-key']['google'])

    def raw_location_keys(self) -> Tuple:
        return 'address_components', 'formatted_address', 'geometery', 'place_id', 'plus_code', 'types'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'google'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address, sensor=False)

