"""Test setup."""

from unittest.mock import AsyncMock

import pytest
from _pytest.logging import LogCaptureFixture
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi import async_migrate_entry, async_setup_entry, async_unload_entry
from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator
from weerlive import WeerliveAPIError

from . import get_mock_config_entry, setup_integration


async def test_setup_and_unload_entry(hass: HomeAssistant) -> None:
    """Test entry setup and unload."""
    config_entry = await setup_integration(hass)

    # Check that the client is stored as runtime_data
    assert isinstance(config_entry.runtime_data, KnmiDataUpdateCoordinator)

    # Unload the entry
    assert await async_unload_entry(hass, config_entry)


async def test_setup_entry_exception(hass: HomeAssistant, mock_weerlive_client: AsyncMock) -> None:
    """Test setup entry raises ConfigEntryNotReady on connection error."""
    # Configure the mock to raise an error on latitude_longitude
    mock_weerlive_client.latitude_longitude.side_effect = WeerliveAPIError()

    # Create config entry but don't set it up through HA's system
    config_entry = get_mock_config_entry()
    config_entry.add_to_hass(hass)

    # This should raise ConfigEntryNotReady due to connection error
    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, config_entry)


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


async def test_async_migrate_entry_v1_to_v2(hass: HomeAssistant, entity_registry: er.EntityRegistry, caplog: LogCaptureFixture) -> None:
    """Test entry migration, v1 to v2."""
    config_entry = await setup_integration(hass)

    hass.config_entries.async_update_entry(config_entry, version=1)
    assert config_entry.version == 1

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
