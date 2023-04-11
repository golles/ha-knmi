"""Tests for knmi api."""
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import pytest

from custom_components.knmi.api import (
    KnmiApiClient,
    KnmiApiClientApiKeyError,
    KnmiApiRateLimitError,
)

from .const import MOCK_CONFIG


async def test_api_key_error(hass: HomeAssistant, aioclient_mock):
    """Test API call exception."""

    api = KnmiApiClient(
        MOCK_CONFIG[CONF_API_KEY],
        MOCK_CONFIG[CONF_LATITUDE],
        MOCK_CONFIG[CONF_LONGITUDE],
        async_get_clientsession(hass),
    )

    aioclient_mock.get(
        "http://weerlive.nl/api/json-data-10min.php?key={}&locatie={},{}".format(
            MOCK_CONFIG[CONF_API_KEY],
            MOCK_CONFIG[CONF_LATITUDE],
            MOCK_CONFIG[CONF_LONGITUDE],
        ),
        text="Vraag eerst een API-key op",
    )

    with pytest.raises(KnmiApiClientApiKeyError):
        await api.async_get_data()


async def test_api_rate_limit_error(hass: HomeAssistant, aioclient_mock):
    """Test API call exception."""

    api = KnmiApiClient(
        MOCK_CONFIG[CONF_API_KEY],
        MOCK_CONFIG[CONF_LATITUDE],
        MOCK_CONFIG[CONF_LONGITUDE],
        async_get_clientsession(hass),
    )

    aioclient_mock.get(
        "http://weerlive.nl/api/json-data-10min.php?key={}&locatie={},{}".format(
            MOCK_CONFIG[CONF_API_KEY],
            MOCK_CONFIG[CONF_LATITUDE],
            MOCK_CONFIG[CONF_LONGITUDE],
        ),
        text="Dagelijkse limiet",
    )

    with pytest.raises(KnmiApiRateLimitError):
        await api.async_get_data()
