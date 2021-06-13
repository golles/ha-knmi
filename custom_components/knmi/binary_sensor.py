"""Binary sensor platform for knmi."""
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    BINARY_SENSOR_ALARM_ICON,
    BINARY_SENSOR_ALARM_NAME,
    DEFAULT_NAME,
    DOMAIN,
)
from .entity import KnmiEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([KnmiBinarySensor(coordinator, entry)])


class KnmiBinarySensor(KnmiEntity, BinarySensorEntity):
    """knmi binary_sensor class."""

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        location = self.coordinator.data["plaats"]
        return f"{DEFAULT_NAME} {location} {BINARY_SENSOR_ALARM_NAME}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data["alarm"] != "0"

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {BINARY_SENSOR_ALARM_NAME: self.coordinator.data["alarmtxt"]}

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return BINARY_SENSOR_ALARM_ICON
