"""Constants for knmi."""

from typing import Final

# API
API_CONF_URL: Final = "https://weerlive.nl/api/toegang/account.php"
API_ENDPOINT: Final = "https://weerlive.nl/api/weerlive_api_v2.php?key={}&locatie={},{}"
API_TIMEOUT: Final = 10
API_TIMEZONE: Final = "Europe/Amsterdam"

# Base component constants.
DOMAIN: Final = "knmi"
NAME: Final = "KNMI"
SUPPLIER: Final = "Weerlive"
VERSION: Final = "2.2.1"

# Defaults
DEFAULT_NAME: Final = NAME
DEFAULT_SCAN_INTERVAL: Final = 300
