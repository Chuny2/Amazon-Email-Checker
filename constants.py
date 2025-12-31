"""
Constants used throughout the Amazon Email Checker application.
Contains mappings between country names and their calling codes.
"""
from dataclasses import dataclass
from typing import Dict, List
import phonenumbers
import pycountry

@dataclass
class Country:
    name: str
    code: str
    region: str  # ISO 3166-1 alpha-2 code

def _generate_country_list() -> List[Country]:
    """
    Dynamically generate the list of supported countries using phonenumbers and pycountry libraries.
    """
    countries = []
    for region_code in phonenumbers.SUPPORTED_REGIONS:
        try:
            country_code = str(phonenumbers.country_code_for_region(region_code))
            
            country_obj = pycountry.countries.get(alpha_2=region_code)
            if country_obj:
                name = country_obj.name.split(' (')[0]
                
                countries.append(Country(name, country_code, region_code))
        except Exception:
            continue
            
    countries.sort(key=lambda x: x.name)
    return countries

COUNTRIES_DATA = _generate_country_list()

# Use names for the UI, but region codes (ISO 3166-1 alpha-2) for internal logic to avoid +1 collisions
COUNTRIES_BY_REGION: Dict[str, Country] = {c.region: c for c in COUNTRIES_DATA}
COUNTRIES_BY_NAME: Dict[str, Country] = {c.name: c for c in COUNTRIES_DATA}
COUNTRY_NAME_TO_REGION = {c.name: c.region for c in COUNTRIES_DATA}
COUNTRY_NAME_TO_CODE = {c.name: c.code for c in COUNTRIES_DATA}

# Security and UI limits
MAX_CORES = 128
MAX_PREFIXES = 50
MAX_PREFIX_LENGTH = 10
MAX_LOG_LINES = 1000
QUEUE_MAX_SIZE = 1000