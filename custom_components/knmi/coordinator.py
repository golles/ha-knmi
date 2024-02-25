"""DataUpdateCoordinator for knmi."""

from datetime import datetime, timedelta
import logging
import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import pytz

from .api import KnmiApiClient
from .const import API_TIMEZONE, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class KnmiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: KnmiApiClient,
        device_info: DeviceInfo,
        scan_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.api = client
        self.device_info = device_info

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            _LOGGER.error("Update failed! - %s", exception)
            raise UpdateFailed() from exception

    def get_value(self, path: list[int | str], default=None) -> Any:
        """
        Get a value from the data by a given path.
        When the value is absent, the default (None) will be returned and an error will be logged.
        """
        value = self.data

        try:
            for key in path:
                value = value[key]

            value_type = type(value).__name__

            if value_type in ["int", "float", "str"]:
                _LOGGER.debug(
                    "Path %s returns a %s (value = %s)", path, value_type, value
                )
            else:
                _LOGGER.debug("Path %s returns a %s", path, value_type)

            return value
        except (IndexError, KeyError):
            _LOGGER.warning("Can't find a value for %s in the API response", path)
            return default

    def get_value_datetime(
        self, path: list[int | str], default=None
    ) -> datetime | None:
        """
        Get a datetime value from the data by a given path.
        When the value is absent, the default (None) will be returned and an error will be logged.
        """
        timezone = pytz.timezone(API_TIMEZONE)
        value = self.get_value(path, default)

        # Timestamp.
        if isinstance(value, int):
            if value > 0:
                _LOGGER.debug("convert %s to datetime (from timestamp)", value)
                return datetime.fromtimestamp(value, tz=timezone)

            return default

        # Time.
        if re.match(r"^\d{2}:\d{2}$", value):
            _LOGGER.debug("convert %s to datetime (from time HH:MM)", value)
            time_array = value.split(":")
            today = datetime.now(timezone)
            return today.replace(
                hour=int(time_array[0]),
                minute=int(time_array[1]),
                second=0,
                microsecond=0,
            )

        # Date.
        if re.match(r"^\d{2}-\d{2}-\d{4}$", value):
            _LOGGER.debug("convert %s to datetime (from date DD-MM-YYYY)", value)
            return timezone.localize(datetime.strptime(value, "%d-%m-%Y"))

        # Date and time.
        if re.match(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$", value):
            _LOGGER.debug(
                "convert %s to datetime (from date and time DD-MM-YYYY HH:MM:SS)", value
            )
            return timezone.localize(datetime.strptime(value, "%d-%m-%Y %H:%M:%S"))

        # Date and time without seconds.
        if re.match(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$", value):
            _LOGGER.debug(
                "convert %s to datetime (from date and time DD-MM-YYYY HH:MM)", value
            )
            return timezone.localize(datetime.strptime(value, "%d-%m-%Y %H:%M"))

        return default
