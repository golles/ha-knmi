"""Test knmi setup process."""

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
import pytest

from custom_components.knmi import (
    async_migrate_entry,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator

from . import setup_component


async def test_setup_unload_and_reload_entry(hass: HomeAssistant, mocked_data):
    """Test entry setup and unload."""
    config_entry = await setup_component(hass)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], KnmiDataUpdateCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], KnmiDataUpdateCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass: HomeAssistant, error_on_get_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = await setup_component(hass)

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_async_migrate_entry_v1_to_v2(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, caplog
):
    """Test entry migration, v1 to v2."""
    config_entry = await setup_component(hass)

    config_entry.version = 1
    assert config_entry.version == 1

    mock_entity_id = "weather.knmi_home"
    entity_registry.async_get_or_create(
        domain="weather",
        platform="knmi",
        unique_id="home",
        config_entry=config_entry,
    )
    assert len(entity_registry.entities) == 1

    assert await async_migrate_entry(hass, config_entry)
    assert len(entity_registry.entities) == 0
    assert f"Deleting version 1 entity: {mock_entity_id}" in caplog.text

    assert config_entry.version == 2
