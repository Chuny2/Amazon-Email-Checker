"""Module for generating random phone numbers for different country codes."""
import random

# Country prefixes lookup dictionary
COUNTRY_PREFIXES = {
    '1': ['2', '3', '4', '5', '6', '7', '8', '9'],  # USA/Canada
    '7': ['9'],  # Russia (mobile numbers start with 9)
    '20': ['10', '11', '12'],  # Egypt
    '27': ['6', '7'],  # South Africa
    '30': ['6'],  # Greece
    '31': ['6'],  # Netherlands
    '32': ['46', '47', '48', '49'],  # Belgium
    '33': ['6', '7'],  # France
    '34': ['6'],  # Spain
    '39': ['3'],  # Italy
    '41': ['7'],  # Switzerland
    '44': ['7'],  # United Kingdom
    '46': ['7'],  # Sweden
    '47': ['4'],  # Norway
    '48': ['5', '6', '7'],  # Poland
    '49': ['15', '16', '17'],  # Germany
    '55': ['9'],  # Brazil
    '60': ['10', '11', '12', '13', '14', '16', '17', '18', '19'],  # Malaysia
    '61': ['4'],  # Australia
    '62': ['8'],  # Indonesia
    '63': ['9'],  # Philippines
    '65': ['8', '9'],  # Singapore
    '66': ['8', '9'],  # Thailand
    '81': ['70', '80', '90'],  # Japan
    '82': ['10', '11'],  # South Korea
    '86': ['13', '14', '15', '17', '18', '19'],  # China
    '90': ['5'],  # Turkey
    '91': ['7', '8', '9'],  # India
    '92': ['3'],  # Pakistan
    '93': ['70', '71', '72', '73', '74', '78', '79'],  # Afghanistan
    '94': ['7'],  # Sri Lanka
    '98': ['9'],  # Iran
    '212': ['6', '7'],  # Morocco
    '213': ['5', '6', '7'],  # Algeria
    '216': ['2', '5', '9'],  # Tunisia
    '218': ['9'],  # Libya
    '234': ['70', '80', '81', '90'],  # Nigeria
    '254': ['7'],  # Kenya
    '255': ['6', '7'],  # Tanzania
    '256': ['7'],  # Uganda
    '260': ['9'],  # Zambia
    '263': ['7'],  # Zimbabwe
    '351': ['9'],  # Portugal
    '964': ['7'],  # Iraq
    '965': ['5', '6'],  # Kuwait
    '966': ['5'],  # Saudi Arabia
    '968': ['9'],  # Oman
    '971': ['50', '52', '54', '55', '56'],  # United Arab Emirates
    '972': ['5'],  # Israel
    '974': ['3', '5', '6', '7'],  # Qatar
}

# Phone number format lengths by country code
# Default is 8 digits after prefix
NUMBER_LENGTHS = {
    '1': 9,    # USA/Canada
    '44': 9,   # UK
    '39': 9,   # Italy
    '55': 8,   # Brazil (also has area code)
    '91': 9,   # India
    '86': 9,   # China
    '7': 9,    # Russia
}

def random_number_sequence(length):
    """Generate a random sequence of digits of specified length."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def generate_phone_number(country_code):
    """
    Generate a random phone number for the given country code.
    
    Args:
        country_code (str): The country code to generate a number for
        
    Returns:
        str: A formatted phone number string with country code
    """
    if country_code not in COUNTRY_PREFIXES:
        return "Country code not supported."

    # Select a random prefix for this country
    prefix = random.choice(COUNTRY_PREFIXES[country_code])
    
    # Get the appropriate length for digits after prefix
    digit_length = NUMBER_LENGTHS.get(country_code, 8)
    
    # Handle special case for Brazil which has an area code
    if country_code == '55':
        area_code = random.randint(10, 99)
        return f"+{country_code}{area_code}{prefix}{random_number_sequence(digit_length)}"
    
    # Standard format for most countries
    return f"+{country_code}{prefix}{random_number_sequence(digit_length)}"