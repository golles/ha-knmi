"""Constants for knmi."""
from datetime import timedelta
from typing import Final

# API
API_ENDPOINT: Final = "http://weerlive.nl/api/json-data-10min.php?key={}&locatie={},{}"
API_TIMEOUT: Final = 10
API_TIMEZONE: Final = "Europe/Amsterdam"

# Base component constants.
NAME: Final = "KNMI"
DOMAIN: Final = "knmi"
VERSION: Final = "1.3.7"

# Defaults
DEFAULT_NAME: Final = NAME
SCAN_INTERVAL = timedelta(seconds=300)

# Platforms.
BINARY_SENSOR: Final = "binary_sensor"
SENSOR: Final = "sensor"
WEATHER: Final = "weather"
PLATFORMS: Final = [BINARY_SENSOR, SENSOR, WEATHER]
