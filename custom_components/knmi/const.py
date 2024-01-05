"""Constants for knmi."""
from typing import Final

# API
API_CONF_URL: Final = "https://weerlive.nl/api/toegang/account.php"
API_ENDPOINT: Final = "https://weerlive.nl/api/json-data-10min.php?key={}&locatie={},{}"
API_TIMEOUT: Final = 10
API_TIMEZONE: Final = "Europe/Amsterdam"

# Base component constants.
NAME: Final = "KNMI"
DOMAIN: Final = "knmi"
VERSION: Final = "1.7.1"

# Defaults
DEFAULT_NAME: Final = NAME
DEFAULT_SCAN_INTERVAL: Final = 300
