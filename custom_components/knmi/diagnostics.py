"""Diagnostics support for knmi."""

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from .coordinator import KnmiDataUpdateCoordinator

TO_REDACT = {CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE}


async def async_get_config_entry_diagnostics(_hass: HomeAssistant, config_entry: ConfigEntry[KnmiDataUpdateCoordinator]) -> dict:
    """Return diagnostics for a config entry."""
    coordinator = config_entry.runtime_data

    return {
        "config_entry": async_redact_data(config_entry.as_dict(), TO_REDACT),
        "data": coordinator.data.to_dict() if coordinator.data else {},
    }
