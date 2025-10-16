"""Custom integration to integrate knmi with Home Assistant.

For more details about this integration, please refer to
https://github.com/golles/ha-knmi/
"""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from weerlive import WeerliveApi

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import KnmiDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.WEATHER]

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry[KnmiDataUpdateCoordinator]) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    api_key = config_entry.data.get(CONF_API_KEY)
    scan_interval_seconds = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    scan_interval = timedelta(seconds=scan_interval_seconds)

    if not api_key:
        msg = "Missing required configuration options: api_key."
        raise ValueError(msg)

    client = WeerliveApi(api_key, async_get_clientsession(hass))

    _LOGGER.debug(
        "Set up entry, with scan_interval of %s seconds",
        scan_interval_seconds,
    )

    config_entry.runtime_data = coordinator = KnmiDataUpdateCoordinator(
        hass=hass,
        client=client,
        scan_interval=scan_interval,
        config_entry=config_entry,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry[KnmiDataUpdateCoordinator]) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry[KnmiDataUpdateCoordinator]) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, config_entry)
    await async_setup_entry(hass, config_entry)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry[KnmiDataUpdateCoordinator]) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        hass.config_entries.async_update_entry(config_entry, version=2)

        entity_registry = er.async_get(hass)
        existing_entries = er.async_entries_for_config_entry(entity_registry, config_entry.entry_id)

        for entry in list(existing_entries):
            _LOGGER.debug("Deleting version 1 entity: %s", entry.entity_id)
            entity_registry.async_remove(entry.entity_id)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True
