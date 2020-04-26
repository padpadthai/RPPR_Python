from typing import Tuple

from geopy import Location, AzureMaps

from app import secrets, config
from app.geocoding.provider import Provider

internal_config = config['geocoders']['azure']


class Azure(Provider):

    def __init__(self):
        self.geocoder = AzureMaps(subscription_key=secrets['api-key']['azure'])

    def raw_location_keys(self) -> Tuple:
        return 'type', 'id', 'score', 'address', 'position', 'viewport', 'entryPoints'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'azure'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address)