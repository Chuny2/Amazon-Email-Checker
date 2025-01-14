import random

def generate_phone_number(country_code):
    """Generate a random phone number for the given country code."""
    prefixes = {
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
    if country_code not in prefixes:
        return "Country code not supported."

    prefix = random.choice(prefixes[country_code])

    def random_number_sequence(length):
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    formats = {
        '1': f"+{country_code}{prefix}{random_number_sequence(9)}",
        '44': f"+{country_code}{prefix}{random_number_sequence(9)}",
        '34': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '49': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '33': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '39': f"+{country_code}{prefix}{random_number_sequence(9)}",
        '61': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '55': f"+{country_code}{random.randint(10, 99)}{prefix}{random_number_sequence(8)}",
        '91': f"+{country_code}{prefix}{random_number_sequence(9)}",
        '81': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '86': f"+{country_code}{prefix}{random_number_sequence(9)}",
        '7': f"+{country_code}{prefix}{random_number_sequence(9)}",
        '27': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '82': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '351': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '32': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '31': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '46': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '47': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '41': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '48': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '30': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '90': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '62': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '60': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '63': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '65': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '66': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '20': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '212': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '213': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '216': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '218': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '234': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '254': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '255': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '256': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '260': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '263': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '94': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '92': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '98': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '972': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '965': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '968': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '974': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '966': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '971': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '93': f"+{country_code}{prefix}{random_number_sequence(8)}",
        '964': f"+{country_code}{prefix}{random_number_sequence(8)}",
    }

    phone_number_str = formats.get(country_code, "Country code not supported.")
    return phone_number_str