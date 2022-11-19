"""
Custom integration to integrate knmi with Home Assistant.

For more details about this integration, please refer to
https://github.com/golles/ha-knmi/
"""
import logging
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KnmiApiClient
from .const import DOMAIN, NAME, PLATFORMS, SCAN_INTERVAL, VERSION

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(_hass: HomeAssistant, _config: Config) -> bool:
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KNMI as config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    api_key = entry.data.get(CONF_API_KEY)
    latitude = entry.data.get(CONF_LATITUDE)
    longitude = entry.data.get(CONF_LONGITUDE)

    session = async_get_clientsession(hass)
    client = KnmiApiClient(api_key, latitude, longitude, session)

    device_info = DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer=NAME,
        name=NAME,
        model=VERSION,
        configuration_url="http://weerlive.nl/api/toegang/account.php",
    )

    coordinator = KnmiDataUpdateCoordinator(
        hass=hass, client=client, device_info=device_info
    )
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            await hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload KNMI config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class KnmiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

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
            raise UpdateFailed() from exception

    def get_value(
        self, key: str, convert_to: Callable = str
    ) -> float | int | str | None:
        """Get a value from the retrieved data and convert to given type"""
        if self.data and key in self.data:
            try:
                return convert_to(self.data.get(key, None))
            except ValueError:
                _LOGGER.warning("Value %s can't be converted to %s", key, convert_to)
                return None

        _LOGGER.warning("Value %s is missing in API response", key)
        return None
