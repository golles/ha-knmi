"""Constants for knmi."""

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
)

# Base component constants.
NAME = "KNMI"
DOMAIN = "knmi"
VERSION = "1.1.2"
ATTRIBUTION = "KNMI Weergegevens via https://weerlive.nl/"

# Platforms.
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
WEATHER = "weather"
PLATFORMS = [BINARY_SENSOR, SENSOR, WEATHER]

# Binary sensors
BINARY_SENSORS = [
    {"name": "Waarschuwing", "unit": "", "icon": "mdi:alert", "key": "alarm"}
]

# Sensors
SENSORS = [
    {"name": "Omschrijving", "unit": "", "icon": "mdi:text", "key": "samenv"},
    {"name": "Korte dagverwachting", "unit": "", "icon": "mdi:text", "key": "verw"},
    {"name": "Dauwpunt", "unit": "°C", "icon": "mdi:thermometer", "key": "dauwp"},
]

# Defaults
DEFAULT_NAME = NAME

# Map weather conditions from KNMI to HA.
CONDITIONS_MAP = {
    "zonnig": ATTR_CONDITION_SUNNY,
    "bliksem": ATTR_CONDITION_LIGHTNING,
    "regen": ATTR_CONDITION_RAINY,
    "buien": ATTR_CONDITION_POURING,
    "hagel": ATTR_CONDITION_HAIL,
    "mist": ATTR_CONDITION_FOG,
    "sneeuw": ATTR_CONDITION_SNOWY,
    "bewolkt": ATTR_CONDITION_CLOUDY,
    "halfbewolkt": ATTR_CONDITION_PARTLYCLOUDY,
    "halfbewolkt_regen": ATTR_CONDITION_PARTLYCLOUDY,
    "zwaarbewolkt": ATTR_CONDITION_CLOUDY,
    "nachtmist": ATTR_CONDITION_FOG,
    "helderenacht": ATTR_CONDITION_CLEAR_NIGHT,
    "wolkennacht": ATTR_CONDITION_CLOUDY,
}

# Map wind direction from KNMI string to number.
WIND_DIRECTION_MAP = {
    "VAR": None,
    "N": 360,
    "Noord": 360,
    "NNO": 22.5,
    "NO": 45,
    "ONO": 67.5,
    "O": 90,
    "Oost": 90,
    "OZO": 112.5,
    "ZO": 135,
    "ZZO": 157.5,
    "Z": 180,
    "Zuid": 180,
    "ZZW": 202.5,
    "ZW": 225,
    "WZW": 247.5,
    "W": 270,
    "West": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5,
}
