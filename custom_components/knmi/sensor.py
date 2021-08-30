"""Sensor platform for knmi."""
from .const import DEFAULT_NAME, DOMAIN, SENSORS
from .entity import KnmiEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[KnmiSensor] = []
    for sensor in SENSORS:
        sensors.append(KnmiSensor(coordinator, entry, sensor["name"], sensor["unit"], sensor["icon"], sensor["key"]))

    async_add_devices(sensors)


class KnmiSensor(KnmiEntity):
    """Knmi Sensor class."""

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
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME} {self.location_name} {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._data_key]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon
