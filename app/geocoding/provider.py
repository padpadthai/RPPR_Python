from typing import Tuple

from geopy import Location


class Provider:

    def raw_location_keys(self) -> Tuple:
        raise NotImplementedError()

    def max_requests(self) -> int:
        raise NotImplementedError()

    def identifier(self) -> str:
        raise NotImplementedError()

    def geocode(self, address) -> Location:
        raise NotImplementedError()
