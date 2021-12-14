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
        sensors.append(
            KnmiBinarySensor(
                coordinator,
                entry,
                sensor.get("name", None),
                sensor.get("icon", None),
                sensor.get("device_class", None),
                sensor.get("attributes", []),
                sensor.get("key", None),
            )
        )

    async_add_devices(sensors)


class KnmiBinarySensor(KnmiEntity, BinarySensorEntity):
    """knmi binary_sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        name,
        icon,
        device_class,
        attributes,
        data_key,
    ):
        super().__init__(coordinator, config_entry)
        self.config_entry = config_entry
        self.location_name = self.coordinator.data["plaats"]
        self._name = name
        self._icon = icon
        self._device_class = device_class
        self._attributes = attributes
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
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attributes = super().extra_state_attributes
        for attribute in self._attributes:
            value = None
            if "key" in attribute:
                value = self.coordinator.data[attribute.get("key", None)]
            if "value" in attribute:
                value = attribute.get("value", None)
            attributes[attribute.get("name", None)] = value

        return attributes
