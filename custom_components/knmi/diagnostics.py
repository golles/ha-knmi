"""Diagnostics support for knmi."""
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from . import DOMAIN, KnmiDataUpdateCoordinator

TO_REDACT = {CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    return {
        "config_entry": async_redact_data(config_entry.as_dict(), TO_REDACT),
        "data": coordinator.data,
    }
