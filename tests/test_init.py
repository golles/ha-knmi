"""Test setup."""

from unittest.mock import AsyncMock, patch

import pytest
from _pytest.logging import LogCaptureFixture
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi import async_migrate_entry, async_setup_entry
from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator
from weerlive import WeerliveAPIError

from . import get_mock_config_entry, setup_integration, unload_integration


async def test_setup_and_unload_entry(hass: HomeAssistant) -> None:
    """Test entry setup and unload."""
    config_entry = await setup_integration(hass)

    # Check that the client is stored as runtime_data
    assert isinstance(config_entry.runtime_data, KnmiDataUpdateCoordinator)

    # Unload the entry
    await unload_integration(hass, config_entry)


async def test_setup_entry_exception(hass: HomeAssistant, mock_weerlive_client: AsyncMock) -> None:
    """Test setup entry raises ConfigEntryNotReady on connection error."""
    # Configure the mock to raise an error on latitude_longitude
    mock_weerlive_client.latitude_longitude.side_effect = WeerliveAPIError()

    # Create config entry and use HA's setup system which properly sets state
    config_entry = get_mock_config_entry()
    config_entry.add_to_hass(hass)

    # This should raise ConfigEntryNotReady due to connection error
    # The setup will fail and raise ConfigEntryNotReady
    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state == ConfigEntryState.SETUP_RETRY


async def test_setup_entry_no_api_key(hass: HomeAssistant) -> None:
    """Test setup entry raises ValueError on connection error."""
    # Create config entry but don't set it up through HA's system
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry",
        data={},
    )
    config_entry.add_to_hass(hass)

    # This should raise ValueError due to missing API key
    with pytest.raises(ValueError):  # noqa: PT011
        await async_setup_entry(hass, config_entry)


async def test_async_reload_entry(hass: HomeAssistant) -> None:
    """Test reloading the entry."""
    # First, set up the integration
    config_entry = await setup_integration(hass)

    # Patch the async_reload_entry at the module level before the listener is triggered
    with patch.object(config_entry, "async_on_unload"), patch("custom_components.knmi.async_reload_entry") as mock_reload_entry:
        # Make the mock_reload_entry async to maintain compatibility
        mock_reload_entry.return_value = None

        # Re-register the update listener which is what we're actually testing
        config_entry.add_update_listener(mock_reload_entry)

        # Update the entry options - this should trigger the reload listener
        hass.config_entries.async_update_entry(config_entry, options={"something": "else"})
        await hass.async_block_till_done()

        # The mock should have been called once
        assert len(mock_reload_entry.call_args_list) == 1


async def test_async_migrate_entry_v1_to_v2(hass: HomeAssistant, entity_registry: er.EntityRegistry, caplog: LogCaptureFixture) -> None:
    """Test entry migration, v1 to v2."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry",
        data={"api_key": "test_key"},
        version=1,
    )
    config_entry.add_to_hass(hass)

    mock_entity_id = "weather.knmi_home"
    entity_registry.async_get_or_create(
        domain="weather",
        platform="knmi",
        unique_id="home",
        config_entry=config_entry,
    )

    assert await async_migrate_entry(hass, config_entry)
    assert len(entity_registry.entities) == 0
    assert f"Deleting version 1 entity: {mock_entity_id}" in caplog.text

    assert config_entry.version == 2
