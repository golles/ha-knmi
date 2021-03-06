"""Constants for knmi tests."""
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

# Mock config data to be used across multiple tests
MOCK_CONFIG = {
    CONF_API_KEY: "abc123xyz000",
    CONF_LATITUDE: 52.354,
    CONF_LONGITUDE: 4.763,
    CONF_NAME: "Home",
}

MOCK_JSON = {"liveweer": [{"plaats": "Purmerend", "temp": "17.5", "gtemp": "16.2", "samenv": "Licht bewolkt", "lv": "86", "windr": "NO", "windrgr": "44", "windms": "3", "winds": "2", "windk": "5.8", "windkmh": "10.8", "luchtd": "1024.0", "ldmmhg": "768", "dauwp": "15", "zicht": "45", "verw": "Geleidelijk meer zonnig, morgen zonnig en droog", "sup": "05:27", "sunder": "22:03", "image": "lichtbewolkt", "d0weer": "bewolkt", "d0tmax": "21", "d0tmin": "14", "d0windk": "2", "d0windknp": "6", "d0windms": "3", "d0windkmh": "11", "d0windr": "ZO", "d0windrgr": "135", "d0neerslag": "0", "d0zon": "14", "d1weer": "halfbewolkt", "d1tmax": "28", "d1tmin": "13", "d1windk": "2", "d1windknp": "4", "d1windms": "2", "d1windkmh": "7", "d1windr": "ZW", "d1windrgr": "225", "d1neerslag": "10", "d1zon": "60", "d2weer": "bewolkt", "d2tmax": "24", "d2tmin": "18", "d2windk": "2", "d2windknp": "6", "d2windms": "3", "d2windkmh": "11", "d2windr": "NW", "d2windrgr": "315", "d2neerslag": "20", "d2zon": "30", "alarm": "0", "alarmtxt": ""}]}
