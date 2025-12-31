"""
This is the math heavy part. We use a Feistel network (like a simplified cipher)
to shuffle phone numbers without having to store them in a list.
Basically, it lets us pick a "random" number from a range [0, N] in O(1) time.
"""
import random
import phonenumbers
from phonenumbers import PhoneNumberType
from constants import COUNTRIES_BY_REGION

def _mix_function(val, r_seed, mask):
    """
    This is the 'mixer' for the shuffle. It just jumbles the bits around
    so the resulting sequence looks random.

    Args:
        val (int): Value to mix.
        r_seed (int): Random seed.
        mask (int): Mask for the shuffle.
    
    Returns:
        int: Mixed value.
    """
    # 0x45d9f3b is a magic constant used for better bit distribution (diffusion)
    val = (val ^ r_seed) * 0x45d9f3b
    val = ((val >> 16) ^ val) * 0x45d9f3b
    val = (val >> 16) ^ val
    return val & mask

def feistel_shuffle(index, range_limit, seed, num_bits, half_bits, mask):
    """
    The core shuffle logic. 
    It 'encrypts' an index to get a new one. If the new one is too big,
    we just try again (cycle walking).

    Args:
        index (int): Index to shuffle.
        range_limit (int): Range limit for the shuffle.
        seed (int): Seed for the shuffle.
        num_bits (int): Number of bits for the shuffle.
        half_bits (int): Half bits for the shuffle.
        mask (int): Mask for the shuffle.
    
    Returns:
        int: Shuffled index.
    """
    curr = index
    for _ in range(100): # Stop after 100 tries to avoid infinite loops
        left = curr >> half_bits
        right = curr & mask
        
        # 4 rounds of swapping and mixing
        for i in range(4):
            new_left = right
            new_right = left ^ _mix_function(right, seed + i, mask)
            left, right = new_left, new_right
            
        curr = (left << half_bits) | right
        if curr < range_limit:
            return curr
    
    # Fallback if the shuffle fails after 100 tries
    return curr % range_limit 

def get_feistel_params(range_limit):
    """
    Calculates the bitmasks we need for the Feistel shuffle based on how 
    many numbers we're scanning.

    Args:
        range_limit (int): Range limit for the shuffle.
    
    Returns:
        tuple: Tuple containing the number of bits, half bits, and mask.
    """
    bits_limit = max(2, range_limit)
    num_bits = (bits_limit - 1).bit_length()
    if num_bits % 2 != 0: 
        num_bits += 1 # Needs to be even to split it in half
    
    half_bits = num_bits // 2
    mask = (1 << half_bits) - 1
    return num_bits, half_bits, mask

def get_valid_starts(region):
    """
    Tries to figure out which digits are actually used for mobile numbers in a country.
    We don't want to waste time scanning numbers that couldn't possibly exist.

    Args:
        region (str): Region of the country.
    
    Returns:
        list: List of valid starting digits for mobile numbers.
    """
    example = phonenumbers.example_number_for_type(region, phonenumbers.PhoneNumberType.MOBILE)
    if not example: 
        # If we can't find an example, we just guess 1-9
        return ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    national_len = len(str(example.national_number))
    country_code = phonenumbers.country_code_for_region(region)
    valid = []
    
    # We check the first two digits to see if they belong to a mobile block
    for digit in "123456789":
        found_for_digit = False
        for second in "0123456789":
            padding = "0" * (national_len - 2)
            test_num = f"+{country_code}{digit}{second}{padding}"
            try:
                parsed = phonenumbers.parse(test_num, region)
                t = phonenumbers.number_type(parsed)
                # Filter for mobile or general mobile blocks
                if t in [PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE]:
                    valid.append(digit)
                    found_for_digit = True
                    break
            except:
                continue
        if found_for_digit:
            continue
            
    return valid if valid else ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

def get_country_config(region, prefix=None):
    """
    Sets up everything we need to know about a country's numbers:
    How many there are, what prefixes to use, and how long they are.

    Args:
        region (str): Region of the country.
        prefix (str, optional): Prefix to use. Defaults to None.
    
    Returns:
        tuple: Tuple containing the total range, prefix map, format type, national length, and country code.
    """
    if region not in COUNTRIES_BY_REGION:
        return 0, [], 0, 0, ""
    
    country = COUNTRIES_BY_REGION[region]
    example = phonenumbers.example_number_for_type(region, phonenumbers.PhoneNumberType.MOBILE)
    if not example: 
        return 0, [], 0, 0, ""
    
    national_len = len(str(example.national_number))
    country_code = country.code
    
    # If the user gave us specific prefixes, we only focus on those
    if prefix:
        p_list = prefix if isinstance(prefix, list) else [p.strip() for p in str(prefix).split(',') if p.strip()]
        if len(p_list) == 1:
            p_str = p_list[0]
            rem_len = national_len - len(p_str)
            if rem_len < 0: 
                return 0, [], 0, 0, ""
            return 10**rem_len, [p_str], 0, national_len, country_code
        else:
            total_range = 0
            p_map = []
            for p in p_list:
                rem_len = national_len - len(p)
                if rem_len >= 0:
                    sub_range = 10**rem_len
                    p_map.append({'prefix': p, 'range': sub_range, 'start': total_range})
                    total_range += sub_range
            return total_range, p_map, 1, national_len, country_code
            
    # If no prefix is given, we find all active mobile blocks
    valid_starts = get_valid_starts(region)
    total_range = 0
    p_map = []
    for s in valid_starts:
        rem_len = national_len - 1
        sub_range = 10**rem_len
        p_map.append({'prefix': s, 'range': sub_range, 'start': total_range})
        total_range += sub_range
        
    return total_range, p_map, 1, national_len, country_code

def format_phone_number(index, config):
    """
    Turns our flat list index back into a E.164 phone number string.

    Args:
        index (int): Index to format.
        config (tuple): Tuple containing the total range, prefix map, format type, national length, and country code.
    
    Returns:
        str: Formatted phone number.
    """
    range_limit, p_data, fmt_type, national_len, country_code = config
    
    if fmt_type == 0:
        p_str = p_data[0]
        rem_len = national_len - len(p_str)
        return f"+{country_code}{p_str}{index:0{rem_len}d}"
    else:
        # Loop through buckets to see which prefix this index belongs to
        for p_info in reversed(p_data):
            if index >= p_info['start']:
                local_idx = index - p_info['start']
                p_str = p_info['prefix']
                rem_len = national_len - len(p_str)
                return f"+{country_code}{p_str}{local_idx:0{rem_len}d}"
    
    return f"+{country_code}{index}"
