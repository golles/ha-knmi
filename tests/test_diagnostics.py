"""Test knmi diagnostics."""

import pytest
from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.components.diagnostics import get_diagnostics_for_config_entry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.diagnostics import TO_REDACT

from . import setup_component, unload_component
from .const import MOCK_ENTRY_ID


@pytest.mark.usefixtures("mocked_data")
async def test_config_entry_diagnostics(hass: HomeAssistant, hass_client: ClientSessionGenerator) -> None:
    """Test config entry diagnostics."""
    config_entry = await setup_component(hass)

    result = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    assert result["config_entry"]["entry_id"] == MOCK_ENTRY_ID
    assert result["config_entry"]["domain"] == DOMAIN

    for key in TO_REDACT:
        assert result["config_entry"]["data"][key] == REDACTED

    assert result["data"]["liveweer"][0]["plaats"] == "Purmerend"

    await unload_component(hass, config_entry)
    await unload_component(hass, config_entry)
    await unload_component(hass, config_entry)
