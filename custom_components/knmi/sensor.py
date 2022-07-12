"""Sensor platform for knmi."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.const import (
    CONF_NAME,
    PERCENTAGE,
    TEMP_CELSIUS,
)
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from . import KnmiDataUpdateCoordinator
from .const import DEFAULT_NAME, DOMAIN

SENSORS: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key="samenv",
        name="Omschrijving",
        icon="mdi:text",
    ),
    SensorEntityDescription(
        key="verw",
        name="Korte dagverwachting",
        icon="mdi:text",
    ),
    SensorEntityDescription(
        key="dauwp",
        name="Dauwpunt",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="gtemp",
        name="Gevoelstemperatuur",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="lv",
        name="Relatieve luchtvochtigheid",
        icon="mdi:water-percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI sensors based on a config entry."""
    async_add_entities(
        KnmiSensor(
            conf_name=entry.data.get(CONF_NAME, hass.config.location_name),
            coordinator=hass.data[DOMAIN][entry.entry_id],
            entry_id=entry.entry_id,
            description=description,
        )
        for description in SENSORS
    )


class KnmiSensor(CoordinatorEntity[KnmiDataUpdateCoordinator], SensorEntity):
    """Defines an KNMI sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize KNMI sensor."""
        super().__init__(coordinator=coordinator)

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{conf_name}_{description.name}".lower()
        )
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {conf_name} {self.name}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key, None)
