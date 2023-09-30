"""DataUpdateCoordinator for knmi."""
import logging
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KnmiApiClient
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER: logging.Logger = logging.getLogger(__package__)


class KnmiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, client: KnmiApiClient, device_info: DeviceInfo
    ) -> None:
        """Initialize."""
        self.api = client
        self.device_info = device_info

        super().__init__(
            hass=hass, logger=_LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            _LOGGER.error("Update failed! - %s", exception)
            raise UpdateFailed() from exception

    def get_value(
        self, key: str, convert_to: Callable = str
    ) -> float | int | str | None:
        """Get a value from the retrieved data and convert to given type"""
        if self.data and key in self.data:
            if self.data.get(key, None) == "" and key != "alarmtxt":
                _LOGGER.warning("Value %s is empty in API response", key)
                return ""  # Leave empty, eg. warning attribute can be an empty string.

            try:
                return convert_to(self.data.get(key, None))
            except ValueError:
                _LOGGER.warning("Value %s can't be converted to %s", key, convert_to)
                return None

        _LOGGER.warning("Value %s is missing in API response", key)
        return None
