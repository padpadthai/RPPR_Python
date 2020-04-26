from typing import Tuple

from geopy import Location, Here as Here_geopy

from app import config, secrets
from app.geocoding.provider import Provider

internal_config = config['geocoders']['here']


class Here(Provider):

    def __init__(self):
        self.geocoder = Here_geopy(apikey=secrets['api-key']['here'])

    def raw_location_keys(self) -> Tuple:
        return 'Relevance', 'MatchLevel', 'MatchQuality', 'MatchType', 'Location'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'here'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address)
