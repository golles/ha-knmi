"""Tests for knmi integration."""

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi.const import DOMAIN

from .const import MOCK_CONFIG, MOCK_ENTRY_ID


async def setup_component(hass: HomeAssistant) -> MockConfigEntry:
    """Setup the custom component for tests."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id=MOCK_ENTRY_ID)
    config_entry.add_to_hass(hass)

    assert await async_setup_component(hass=hass, domain=DOMAIN, config=MOCK_CONFIG)
    await hass.async_block_till_done()

    return config_entry


async def unload_component(hass: HomeAssistant, config_entry: MockConfigEntry) -> MockConfigEntry:
    """Unload the custom component for tests."""
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
