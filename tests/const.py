"""Constants for knmi tests."""

from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)

# Mock config data to be used across multiple tests
MOCK_CONFIG = {
    CONF_API_KEY: "abc123xyz000",
    CONF_LATITUDE: 52.354,
    CONF_LONGITUDE: 4.763,
    CONF_NAME: "Home",
}

MOCK_ENTRY_ID = "test"

MOCK_UPDATE_CONFIG = {CONF_SCAN_INTERVAL: 600}
