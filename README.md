# Amazon Email and Number Checker

A Python GUI application for validating email addresses and phone numbers against Amazon's authentication system. Built with PyQt6, this tool supports multi-threaded operations and includes a phone number generator for multiple countries.

## Features

- Dark-themed GUI
- Multi-threaded validation
- Email and phone number validation
- Supports 40+ countries
- Batch processing and auto-save

## Requirements

```bash
pip install PyQt6 requests
```

## Usage

1. Clone the repository:
```bash
git clone https://github.com/chuny2/Amazon-Email-Checker.git
cd Amazon-Email-Checker
```

2. Run the application:
```bash
python3 AmazonBot.py
```

## Email Validation

1. Click "Browse Email List" to select a file.
2. Enter the number of cores.
3. Wait until it's done.

## Phone Number Validation

1. Select a country.
2. Enter the number of cores.
3. Click "Generate Numbers."

## Results

- Saved automatically:
  - Emails: `Valid.txt`
  - Phones: `Valid_[CountryCode].txt`

## Adding New Countries

1. Open `phone_number_generator.py`.
2. Add the country code and prefixes to `prefixes`:
   ```python
   prefixes = {
       '999': ['1', '2', '3'],
   }
   ```
   - `999` is the country code.
   - `['1', '2', '3']` are the possible starting digits for phone numbers in that country.

3. Add the format to `formats`:
   ```python
   formats = {
       '999': f"+{country_code}{prefix}{random_number_sequence(8)}",
   }
   ```
   - `formats` defines how phone numbers are structured for each country.
   - Use `+{country_code}` for the international code, `{prefix}` for the starting digits, and `{random_number_sequence(n)}` for the rest of the number.

4. Update constants.py to include the new country:
    ```python
    country_codes = {
      'NewCountry': '999',
    }
    ```
    - Replace 'NewCountry' with the country name.
    - Replace '999' with the new country code.

5. Save and restart the app.

## Disclaimer

This application interacts with Amazon's authentication system by simulating requests. To keep it functional, ensure that cookies, headers, and request data in the `Amazon` class (in `amazon_auth.py`) are updated regularly to reflect any changes in Amazon's system. These include session tokens, user-agent strings, and other necessary fields in headers and cookies.

Be aware that using this tool may violate Amazon's terms of service, and it is your responsibility to use it appropriately.
