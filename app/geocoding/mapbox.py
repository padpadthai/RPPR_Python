from typing import Tuple

from app import config, secrets

from geopy import Location, MapBox as MapBox_geopy

from app.geocoding.provider import Provider

internal_config = config['geocoders']['mapbox']


class MapBox(Provider):

    def __init__(self):
        self.geocoder = MapBox_geopy(api_key=secrets['api-key']['mapbox'])

    def raw_location_keys(self) -> Tuple:
        return 'type', 'relevance', 'properties', 'place_name', 'center', 'geometry', 'context'

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'mapbox'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address, country="IE")
