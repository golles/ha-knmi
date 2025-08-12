"""Test for config flow."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.knmi.const import DOMAIN
from weerlive import WeerliveAPIConnectionError, WeerliveAPIKeyError, WeerliveAPIRateLimitError

from . import get_mock_config_data, setup_integration, unload_integration

MOCK_UPDATE_CONFIG = {CONF_SCAN_INTERVAL: 600}


@pytest.fixture(autouse=True, name="bypass_setup")
def fixture_bypass_setup_fixture() -> Generator[None]:
    """Prevent actual setup of the integration during tests."""
    with patch("custom_components.knmi.async_setup_entry", return_value=True):
        yield


async def test_successful_config_flow(hass: HomeAssistant) -> None:
    """Test a successful config flow."""
    config_data = get_mock_config_data()
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to fill in all fields, it would result in this function call
    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=config_data)

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == config_data[CONF_NAME]
    assert result2["data"] == config_data
    assert result2["result"]


@pytest.mark.parametrize(
    ("side_effect", "error"),
    [
        (WeerliveAPIConnectionError, "general"),
        (WeerliveAPIKeyError, "api_key"),
        (WeerliveAPIRateLimitError, "daily_limit"),
    ],
)
async def test_unsuccessful_config_flow(side_effect: Exception, error: str, hass: HomeAssistant, mock_weerlive_client: AsyncMock) -> None:
    """Test an unsuccessful config flow ."""
    config_data = get_mock_config_data()
    mock_weerlive_client.latitude_longitude.side_effect = side_effect

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to fill in an incomplete form, it would result in this function call
    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=config_data)

    # Check that the config flow returns the error
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": error}


async def test_step_reconfigure(hass: HomeAssistant) -> None:
    """Test for reconfigure step."""
    updated_data = {
        CONF_API_KEY: "1234567890",
        CONF_LATITUDE: 52.354,
        CONF_LONGITUDE: 4.763,
        CONF_NAME: "Home2",
    }
    config_entry = await setup_integration(hass)

    result = await config_entry.start_reconfigure_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=updated_data,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"

    assert config_entry.title == updated_data[CONF_NAME]
    assert config_entry.data == {**updated_data}


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test an options flow."""
    # Create a new MockConfigEntry and add to HASS (we're bypassing config
    # flow entirely)
    config_entry = await setup_integration(hass)

    # Initialize an options flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Verify that the first options step is a user form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Enter some fake data into the form
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=MOCK_UPDATE_CONFIG,
    )

    # Verify that the flow finishes
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == get_mock_config_data()[CONF_NAME]

    # Verify that the options were updated
    assert config_entry.options == MOCK_UPDATE_CONFIG

    await unload_integration(hass, config_entry)
