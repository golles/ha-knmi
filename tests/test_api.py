"""Tests for knmi api."""
import asyncio

import aiohttp
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.knmi.api import KnmiApiClient

from .const import MOCK_CONFIG


async def test_api(hass, aioclient_mock, caplog):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = KnmiApiClient(
        MOCK_CONFIG[CONF_API_KEY],
        MOCK_CONFIG[CONF_LATITUDE],
        MOCK_CONFIG[CONF_LONGITUDE],
        async_get_clientsession(hass),
    )

    # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
    # to mock responses to aiohttp requests. In this case we are telling the mock to
    # return {"test": "test"} when a `GET` call is made to the specified URL. We then
    # call `async_get_data` which will make that `GET` request.
    aioclient_mock.get(
        f"http://weerlive.nl/api/json-data-10min.php?key={MOCK_CONFIG[CONF_API_KEY]}&locatie={MOCK_CONFIG[CONF_LATITUDE]},{MOCK_CONFIG[CONF_LONGITUDE]}",
        json={"liveweer": [{"weather": "good"}]},
    )
    assert await api.async_get_data() == {"weather": "good"}
