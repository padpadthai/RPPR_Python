import logging
import re

from app.property_price_register import RawPropertySale


class Sanitiser:

    def __init__(self, raw_property_sale: RawPropertySale):
        # deep copying could be nice but expensive
        self.__raw_property_sale = raw_property_sale

    def sanitise(self) -> RawPropertySale:
        sale = self.__raw_property_sale
        sale.address = self.sanitise_address(sale.address, sale.app_id)
        sale.postcode = self.sanitise_postcode(sale.postcode, sale.app_id)
        sale.price = self.sanitise_price(sale.price, sale.app_id)
        sale.property_description = self.sanitise_property_description(sale.property_description, sale.app_id)
        sale.size_description = self.sanitise_size_description(sale.size_description, sale.app_id)
        return sale

    regexes = {
        'postcode': {
            'dublin': {
                'bearla': re.compile(r'Dublin'),
                'gaeilge': re.compile(r'Baile .tha Cliath')
            },
            'none': {
                'gaeilge': re.compile(r'Ní Bhaineann')
            }
        },
        'price': re.compile(r'(€(\d+,?)*.\d{2})'),
        'description': {
            'new': {
                'bearla': re.compile(r'New Dwelling house /Apartment'),
                'gaeilge': re.compile(r'Teach/.ras.n C.naithe Nua')
            },
            'used': {
                'bearla': re.compile(r'Second-Hand Dwelling house /Apartment'),
                'gaeilge': re.compile(r'Teach/Árasán Cónaithe Atháimhe')
            }
        },
        'size': {
            'large': {
                'bearla': re.compile(r'greater than( or equal to)? 125 sq metres')
            },
            'medium': {
                'bearla': re.compile(r'greater than or equal to 38 sq metres and less than 125 sq metres'),
                'gaeilge': re.compile(r'níos mó ná nó cothrom le 38 méadar cearnach agus níos lú ná 125 méadar cearnach')
            },
            'small': {
                'bearla': re.compile(r'less than 38 sq metres'),
                'gaeilge': re.compile(r'n.os l. n. 38 m.adar cearnach')
            }
        }
    }

    # TODO: very complex and may be clearer after geocoding
    @classmethod
    def sanitise_address(cls, address: str, identifier: str = None) -> str:
        return address

    @classmethod
    def sanitise_postcode(cls, postcode: str, identifier: str = None) -> str:
        if cls.regexes['postcode']['dublin']['gaeilge'].match(postcode):
            # logging.debug("Sanitising '{}' of '{}'".format(postcode, identifier))
            return cls.regexes['postcode']['dublin']['gaeilge'].sub('Dublin', postcode)
        elif cls.regexes['postcode']['none']['gaeilge'].match(postcode):
            # logging.debug("Sanitising '{}' of '{}'".format(postcode, identifier))
            return cls.regexes['postcode']['none']['gaeilge'].sub('', postcode)
        elif len(postcode) > 0 and cls.regexes['postcode']['dublin']['bearla'].match(postcode) is None:
            logging.warning("Unusual postcode '{}' of '{}'".format(postcode, identifier))
        return postcode

    @classmethod
    def sanitise_price(cls, price: str, identifier: str = None) -> str:
        if cls.regexes['price'].match(price) is None:
            logging.warning("Unusual price '{}' of '{}'".format(price, identifier))
        return price

    @classmethod
    def sanitise_property_description(cls, property_description: str, identifier: str = None) -> str:
        if cls.regexes['description']['new']['gaeilge'].match(property_description):
            # logging.debug("Sanitising '{}' of '{}'".format(property_description, identifier))
            return cls.regexes['description']['new']['gaeilge'].sub('New Dwelling house /Apartment',
                                                                    property_description)
        elif cls.regexes['description']['used']['gaeilge'].match(property_description):
            # logging.debug("Sanitising '{}' of '{}'".format(property_description, identifier))
            return cls.regexes['description']['used']['gaeilge'].sub('Second-Hand Dwelling house /Apartment',
                                                                     property_description)
        elif cls.regexes['description']['new']['bearla'].match(property_description) is None and \
                cls.regexes['description']['used']['bearla'].match(property_description) is None:
            logging.warning("Unusual property description '{}' of '{}'".format(property_description, identifier))
        return property_description

    @classmethod
    def sanitise_size_description(cls, size_description: str, identifier: str = None) -> str:
        if cls.regexes['size']['large']['bearla'].match(size_description):
            # logging.debug("Sanitising '{}' of '{}'".format(size_description, identifier))
            return cls.regexes['size']['large']['bearla'].sub('greater than or equal to 125 sq metres',
                                                              size_description)
        elif cls.regexes['size']['medium']['gaeilge'].match(size_description):
            # logging.debug("Sanitising '{}' of '{}'".format(size_description, identifier))
            return cls.regexes['size']['medium']['gaeilge'] \
                .sub('greater than or equal to 38 sq metres and less than 125 sq metres', size_description)
        elif cls.regexes['size']['small']['gaeilge'].match(size_description):
            # logging.debug("Sanitising '{}' of '{}'".format(size_description, identifier))
            return cls.regexes['size']['small']['gaeilge'].sub('less than 38 sq metres', size_description)
        elif len(size_description) > 0 and \
                cls.regexes['size']['large']['bearla'].match(size_description) is None and \
                cls.regexes['size']['medium']['bearla'].match(size_description) is None and \
                cls.regexes['size']['small']['bearla'].match(size_description) is None:
            logging.warning("Unusual size description '{}' of '{}'".format(size_description, identifier))
        return size_description
