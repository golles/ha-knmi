"""DataUpdateCoordinator for knmi."""

import logging
from datetime import timedelta
from typing import Self

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from weerlive import Response, WeerliveApi

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class KnmiDataUpdateCoordinator(DataUpdateCoordinator[Response]):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry[Self]

    def __init__(
        self,
        hass: HomeAssistant,
        client: WeerliveApi,
        scan_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.client = client

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> Response:
        """Update data via library."""
        latitude = self.config_entry.data.get(CONF_LATITUDE)
        longitude = self.config_entry.data.get(CONF_LONGITUDE)

        if latitude is None or longitude is None:
            raise UpdateFailed

        try:
            return await self.client.latitude_longitude(latitude=float(latitude), longitude=float(longitude))
        except Exception as exception:
            raise UpdateFailed from exception
