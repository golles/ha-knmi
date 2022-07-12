"""Constants for knmi."""

from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
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

# API
API_ENDPOINT = "http://weerlive.nl/api/json-data-10min.php?key={}&locatie={},{}"
API_TIMEOUT = 10

# Base component constants.
NAME = "KNMI"
DOMAIN = "knmi"
VERSION = "1.1.11"
ATTRIBUTION = "KNMI Weergegevens via https://weerlive.nl/"

# Defaults
DEFAULT_NAME = NAME

# Platforms.
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
WEATHER = "weather"
PLATFORMS = [BINARY_SENSOR, SENSOR, WEATHER]

# Binary sensors
BINARY_SENSORS = [
    {
        "name": "Waarschuwing",
        "unit": "",
        "icon": "mdi:alert",
        "key": "alarm",
        "device_class": BinarySensorDeviceClass.SAFETY,
        "attributes": [
            {
                "name": "Waarschuwing",
                "key": "alarmtxt",
            },
        ],
    },
]

# Sensors
SENSORS = [
    {
        "name": "Omschrijving",
        "icon": "mdi:text",
        "key": "samenv",
    },
    {
        "name": "Korte dagverwachting",
        "icon": "mdi:text",
        "key": "verw",
    },
    {
        "name": "Dauwpunt",
        "unit_of_measurement": TEMP_CELSIUS,
        "icon": "mdi:thermometer",
        "key": "dauwp",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "name": "Gevoelstemperatuur",
        "unit_of_measurement": TEMP_CELSIUS,
        "icon": "mdi:thermometer",
        "key": "gtemp",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "name": "Relatieve luchtvochtigheid",
        "unit_of_measurement": PERCENTAGE,
        "icon": "mdi:water-percent",
        "key": "lv",
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
]

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
