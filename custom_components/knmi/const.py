"""Constants for knmi."""

from typing import Final
from datetime import timedelta
import logging

# API
API_ENDPOINT: Final = "http://weerlive.nl/api/json-data-10min.php?key={}&locatie={},{}"
API_TIMEOUT: Final = 10

# Base component constants.
NAME: Final = "KNMI"
DOMAIN: Final = "knmi"
VERSION: Final = "1.1.11"

# Defaults
_LOGGER: logging.Logger = logging.getLogger(__package__)
DEFAULT_NAME: Final = NAME
SCAN_INTERVAL = timedelta(seconds=300)

# Platforms.
BINARY_SENSOR: Final = "binary_sensor"
SENSOR: Final = "sensor"
WEATHER: Final = "weather"
PLATFORMS: Final = [BINARY_SENSOR, SENSOR, WEATHER]
