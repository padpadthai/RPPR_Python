from typing import Tuple

from app import config
from app.geocoding.provider import Provider

from geopy import Location, ArcGIS as ArcGIS_geopy

internal_config = config['geocoders']['arcgis']


class ArcGIS(Provider):

    def __init__(self):
        self.geocoder = ArcGIS_geopy()

    def raw_location_keys(self) -> Tuple:
        return tuple(['score'])

    def max_requests(self) -> int:
        return internal_config['max-requests']

    def identifier(self) -> str:
        return 'arcgis'

    def geocode(self, address) -> Location:
        return self.geocoder.geocode(address)
