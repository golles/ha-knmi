"""Test knmi setup process."""

import pytest
from _pytest.logging import LogCaptureFixture
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er

from custom_components.knmi import async_migrate_entry, async_reload_entry, async_setup_entry, async_unload_entry
from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator

from . import setup_component, unload_component


@pytest.mark.usefixtures("mocked_data")
async def test_setup_unload_and_reload_entry(hass: HomeAssistant) -> None:
    """Test entry setup and unload."""
    config_entry = await setup_component(hass)
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(hass.data[DOMAIN][config_entry.entry_id], KnmiDataUpdateCoordinator)

    # Reload the entry and assert that the data from above is still there
    await async_reload_entry(hass, config_entry)
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(hass.data[DOMAIN][config_entry.entry_id], KnmiDataUpdateCoordinator)

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.usefixtures("error_on_get_data")
async def test_setup_entry_exception(hass: HomeAssistant) -> None:
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = await setup_component(hass)

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)

    await unload_component(hass, config_entry)


async def test_async_migrate_entry_v1_to_v2(hass: HomeAssistant, entity_registry: er.EntityRegistry, caplog: LogCaptureFixture) -> None:
    """Test entry migration, v1 to v2."""
    config_entry = await setup_component(hass)

    hass.config_entries.async_update_entry(config_entry, version=1)
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
    assert config_entry.version == 2
