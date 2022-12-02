"""Tests for knmi api."""
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import pytest

from custom_components.knmi.api import KnmiApiClient, KnmiApiException

from .const import MOCK_CONFIG, MOCK_JSON


@pytest.mark.asyncio
async def test_api_success(hass, aioclient_mock, caplog):
    """Test successful API call."""

    # To test the api submodule, we first create an instance of our API client
    api = KnmiApiClient(
        MOCK_CONFIG[CONF_API_KEY],
        MOCK_CONFIG[CONF_LATITUDE],
        MOCK_CONFIG[CONF_LONGITUDE],
        async_get_clientsession(hass),
    )

    # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
    # to mock responses to aiohttp requests. In this case we are telling the mock to
    # return `MOCK_JSON` when a `GET` call is made to the specified URL. We then
    # call `async_get_data` which will make that `GET` request.
    aioclient_mock.get(
        f"http://weerlive.nl/api/json-data-10min.php?key={MOCK_CONFIG[CONF_API_KEY]}&locatie={MOCK_CONFIG[CONF_LATITUDE]},{MOCK_CONFIG[CONF_LONGITUDE]}",
        json=MOCK_JSON,
    )

    response = await api.async_get_data()
    assert response == MOCK_JSON["liveweer"][0]


@pytest.mark.asyncio
async def test_api_exceptions(hass, aioclient_mock, caplog):
    """Test API call exception."""

    api = KnmiApiClient(
        MOCK_CONFIG[CONF_API_KEY],
        MOCK_CONFIG[CONF_LATITUDE],
        MOCK_CONFIG[CONF_LONGITUDE],
        async_get_clientsession(hass),
    )

    aioclient_mock.get(
        f"http://weerlive.nl/api/json-data-10min.php?key={MOCK_CONFIG[CONF_API_KEY]}&locatie={MOCK_CONFIG[CONF_LATITUDE]},{MOCK_CONFIG[CONF_LONGITUDE]}",
        json="Vraag eerst een API-key op",
    )

    with pytest.raises(KnmiApiException):
        await api.async_get_data()

    aioclient_mock.get(
        f"http://weerlive.nl/api/json-data-10min.php?key={MOCK_CONFIG[CONF_API_KEY]}&locatie={MOCK_CONFIG[CONF_LATITUDE]},{MOCK_CONFIG[CONF_LONGITUDE]}",
        json="Exceeded Daily Limit",
    )

    with pytest.raises(KnmiApiException):
        await api.async_get_data()
