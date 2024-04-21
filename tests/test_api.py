"""Tests for knmi api."""

from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.knmi.api import (
    KnmiApiClient,
    KnmiApiClientApiKeyError,
    KnmiApiClientError,
    KnmiApiRateLimitError,
)
from custom_components.knmi.const import API_ENDPOINT

from . import setup_component
from .const import MOCK_CONFIG


@pytest.mark.parametrize(
    "error_text, exception",
    [
        ("Vraag eerst een API-key op", KnmiApiClientApiKeyError),
        ("Dagelijkse limiet", KnmiApiRateLimitError),
    ],
)
async def test_api_error(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    error_text: str,
    exception: KnmiApiClientError,
):
    """Test API call error."""

    api = KnmiApiClient(
        MOCK_CONFIG[CONF_API_KEY],
        MOCK_CONFIG[CONF_LATITUDE],
        MOCK_CONFIG[CONF_LONGITUDE],
        async_get_clientsession(hass),
    )

    aioclient_mock.get(
        API_ENDPOINT.format(
            MOCK_CONFIG[CONF_API_KEY],
            MOCK_CONFIG[CONF_LATITUDE],
            MOCK_CONFIG[CONF_LONGITUDE],
        ),
        text=error_text,
    )

    with pytest.raises(exception):
        await api.async_get_data()


@pytest.mark.fixture("_.json")
async def test_invalid_json_fix(hass: HomeAssistant, mocked_data):
    """Test for fix https://github.com/golles/ha-knmi/issues/130."""
    config_entry = await setup_component(hass)

    state = hass.states.get("sensor.knmi_air_pressure")
    assert state.state == "unknown"

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()
