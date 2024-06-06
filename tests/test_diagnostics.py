"""Test knmi diagnostics."""

from http import HTTPStatus
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util.json import JsonObjectType
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.diagnostics import TO_REDACT

from . import setup_component, unload_component
from .const import MOCK_ENTRY_ID


async def test_config_entry_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mocked_data,
) -> None:
    """Test config entry diagnostics."""
    config_entry = await setup_component(hass)

    result = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    assert result["config_entry"]["entry_id"] == MOCK_ENTRY_ID
    assert result["config_entry"]["domain"] == DOMAIN

    for key in TO_REDACT:
        assert result["config_entry"]["data"][key] == "**REDACTED**"

    assert result["data"]["liveweer"][0]["plaats"] == "Purmerend"

    await unload_component(hass, config_entry)


# The following 2 functions are copied from https://github.com/home-assistant/core/blob/dev/tests/components/diagnostics/__init__.py
async def _get_diagnostics_for_config_entry(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    config_entry: ConfigEntry,
) -> JsonObjectType:
    """Return the diagnostics config entry for the specified domain."""
    assert await async_setup_component(hass, "diagnostics", {})
    await hass.async_block_till_done()

    client = await hass_client()
    response = await client.get(
        f"/api/diagnostics/config_entry/{config_entry.entry_id}"
    )
    assert response.status == HTTPStatus.OK
    return cast(JsonObjectType, await response.json())


async def get_diagnostics_for_config_entry(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    config_entry: ConfigEntry,
) -> JsonObjectType:
    """Return the diagnostics config entry for the specified domain."""
    data = await _get_diagnostics_for_config_entry(hass, hass_client, config_entry)
    return cast(JsonObjectType, data["data"])
