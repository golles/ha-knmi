"""
Custom integration to integrate knmi with Home Assistant.

For more details about this integration, please refer to
https://github.com/golles/ha-knmi/
"""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .api import KnmiApiClient
from .const import API_CONF_URL, DEFAULT_SCAN_INTERVAL, DOMAIN, NAME, SUPPLIER, VERSION
from .coordinator import KnmiDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.WEATHER,
]

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    api_key = entry.data.get(CONF_API_KEY)
    latitude = entry.data.get(CONF_LATITUDE)
    longitude = entry.data.get(CONF_LONGITUDE)
    scan_interval_seconds = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    scan_interval = timedelta(seconds=scan_interval_seconds)

    session = async_get_clientsession(hass)
    client = KnmiApiClient(api_key, latitude, longitude, session)

    _LOGGER.debug(
        "Set up entry, with scan_interval of %s seconds",
        scan_interval_seconds,
    )

    device_info = DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=SUPPLIER,
        name=NAME,
        sw_version=VERSION,
        configuration_url=API_CONF_URL,
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator = KnmiDataUpdateCoordinator(
        hass=hass,
        client=client,
        device_info=device_info,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        # Replace with the following line after 2024.3.
        # hass.config_entries.async_update_entry(config_entry, version=2)
        # See https://developers.home-assistant.io/blog/2024/02/12/async_update_entry/
        config_entry.version = 2

        registry = entity_registry.async_get(hass)

        for entry in list(registry.entities.values()):
            _LOGGER.debug("Deleting old entity %s", entry.entity_id)
            registry.async_remove(entry.entity_id)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True
