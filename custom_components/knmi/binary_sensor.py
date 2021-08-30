"""Binary sensor platform for knmi."""
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    BINARY_SENSORS,
    DEFAULT_NAME,
    DOMAIN,
)
from .entity import KnmiEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors: list[KnmiBinarySensor] = []
    for sensor in BINARY_SENSORS:
        sensors.append(KnmiBinarySensor(coordinator, entry, sensor["name"], sensor["unit"], sensor["icon"], sensor["key"]))

    async_add_devices(sensors)


class KnmiBinarySensor(KnmiEntity, BinarySensorEntity):
    """knmi binary_sensor class."""

    def __init__(
        self, coordinator, config_entry, name, unit_of_measurement, icon, data_key
    ):
        super().__init__(coordinator, config_entry)
        self.config_entry = config_entry
        self.location_name = self.coordinator.data["plaats"]
        self._name = name
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._data_key = data_key

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return f"{DEFAULT_NAME} {self.location_name} {self._name}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data[self._data_key] != "0"

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {self._name: self.coordinator.data["alarmtxt"]}

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon
