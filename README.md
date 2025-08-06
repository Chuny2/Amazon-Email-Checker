# Amazon Email & Phone Number Checker

A Python application with GUI for checking the validity of emails and phone numbers on Amazon.

## Features

- **Email Validation**: Check a list of emails against Amazon to find valid accounts
- **Phone Number Generator**: Generate and validate random phone numbers for different countries
- **Multi-threaded Processing**: Utilize multiple CPU cores for faster validation
- **Live Results**: View results in real-time through the GUI
- **Dark Theme Interface**: User-friendly dark-themed interface
- **Progress Tracking**: Monitor validation progress, speed, and success rates

## Preview

Here’s a demo of the application in action:

![Demo of the Application](AmazonGif.gif)

## Requirements

- Python 3.6+
- PyQt6
- Amazon authentication library (amazon_auth.py)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/chuny2/Amazon-Email-Checker.git
cd Amazon-Email-Checker
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python AmazonBot.py
```

## Usage

### Checking Email Lists

1. Launch the application using `python AmazonBot.py`
2. Enter the number of CPU cores to use for checking
3. Click "Browse Email List" and select a .txt file containing emails (one per line)
4. The application will check each email and display results in real-time
5. Valid emails will be saved to `Valid.txt`

### Generating & Checking Phone Numbers

1. Launch the application 
2. Enter the number of CPU cores to use
3. Select a country from the dropdown menu
4. Click "Generate Numbers" to start generating and checking random phone numbers
5. Valid phone numbers will be saved to `Valid_{country_code}.txt`

### Stopping Operations

- Click "Cancel Operations" to stop any ongoing checking process
- Results found before cancellation will still be saved

## File Structure

- `AmazonBot.py` - Main entry point for the application
- `gui.py` - GUI implementation using PyQt6
- `utils.py` - Core functionality for email/number checking
- `utils_io.py` - File operations utilities for safe reading/writing
- `phone_number_generator.py` - Generate random phone numbers by country
- `constants.py` - Contains country code mappings and other constants

## Adding New Phone Number Formats

The application supports generating phone numbers for various countries. Each country follows specific phone number formats. Here's how to add or modify country phone number formats:

### Understanding the Phone Number Structure

Phone numbers in this application follow this general structure:
```
+[COUNTRY_CODE][PREFIX][RANDOM_DIGITS]
```

For example, a US number might look like: `+1 234 5678901`
- `+1` is the country code
- `234` is the prefix
- `5678901` are random digits

### Step-by-Step Guide to Add a New Country

1. **Locate Key Files:**
   - `phone_number_generator.py` - Contains phone number generation logic
   - `constants.py` - Contains country names and codes for the UI

2. **Add Country Prefixes:**
   Open `phone_number_generator.py` and find the `COUNTRY_PREFIXES` dictionary. Add your new country code with its prefixes:

   ```python
   # For Mexico (country code 52)
   'COUNTRY_PREFIXES = {
       // ...existing code...
       '52': ['1', '55', '81'],  # Mexico: 1 for mobile, 55 for Mexico City, 81 for Monterrey
   }
   ```

3. **Specify Number Length:**
   Find the `NUMBER_LENGTHS` dictionary and add the number of digits after the prefix:

   ```python
   NUMBER_LENGTHS = {
       // ...existing code...
       '52': 8,  # Mexican numbers have 8 digits after prefix for mobile
   }
   ```

4. **Add to UI Dropdown:**
   Open `constants.py` and add the country to the `country_codes` dictionary:

   ```python
   country_codes = {
       // ...existing code...
       'Mexico': '52',
   }
   ```

5. **Special Cases:**
   If your country has a special format (like area codes), you'll need to add a condition in the `generate_phone_number()` function:

   ```python
   # Example for Colombia (country code 57) with city codes
   if country_code == '57':
       city_code = random.choice(['1', '2', '4', '5'])  # Bogotá, Medellín, Cali, Barranquilla
       return f"+{country_code}{city_code}{random_number_sequence(7)}"
   ```

### Real Examples

**Example 1: Adding Support for Argentina (country code 54)**

```python
# In phone_number_generator.py
COUNTRY_PREFIXES['54'] = ['9', '11', '351', '341']  # 9 for mobile, others for city codes
NUMBER_LENGTHS['54'] = 8  # 8 digits after prefix

# In constants.py
country_codes['Argentina'] = '54'
```

This would generate numbers like:
- `+549xxxxxxxx` (mobile)
- `+5411xxxxxxxx` (Buenos Aires)

**Example 2: Adding Support for New Zealand (country code 64)**

```python
# In phone_number_generator.py
COUNTRY_PREFIXES['64'] = ['21', '22', '27', '29']  # Mobile prefixes
NUMBER_LENGTHS['64'] = 7  # 7 digits after mobile prefix

# Special case in generate_phone_number() function
if country_code == '64':
    if prefix.startswith('2'):  # Mobile numbers
        return f"+{country_code}{prefix}{random_number_sequence(7)}"
    else:  # Landline numbers
        area_code = random.choice(['3', '4', '6', '7', '9'])
        return f"+{country_code}{area_code}{random_number_sequence(6)}"

# In constants.py
country_codes['New Zealand'] = '64'
```

After adding these changes, the new countries will appear in the dropdown menu, and the application will generate valid-format phone numbers when those countries are selected.

## Disclaimer

Be aware that using this tool may violate Amazon's terms of service, and it is your responsibility to use it appropriately.
