"""Binary sensor platform for knmi."""

from collections.abc import Mapping
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.components.sensor import (
    SensorEntityDescription,
)
from homeassistant.components.binary_sensor import (
    DOMAIN as SENSOR_DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from . import KnmiDataUpdateCoordinator
from .const import DEFAULT_NAME, DOMAIN

ALARM_SENSOR = SensorEntityDescription(
    key="alarm",
    name="Waarschuwing",
    icon="mdi:alert",
    device_class=BinarySensorDeviceClass.SAFETY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI binary sensors based on a config entry."""
    async_add_entities(
        [
            KnmiBinaryAlarmSensor(
                conf_name=entry.data.get(CONF_NAME, hass.config.location_name),
                coordinator=hass.data[DOMAIN][entry.entry_id],
                entry_id=entry.entry_id,
                description=ALARM_SENSOR,
            )
        ]
    )


class KnmiBinarySensor(
    CoordinatorEntity[KnmiDataUpdateCoordinator], BinarySensorEntity
):
    """Defines an KNMI binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize KNMI binary sensor."""
        super().__init__(coordinator=coordinator)

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{conf_name}_{description.name}".lower()
        )
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}-{self.name}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the entity is on."""
        return self.coordinator.data.get(self.entity_description.key, None) != "0"


class KnmiBinaryAlarmSensor(KnmiBinarySensor):
    """Defines an KNMI alarm binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize KNMI binary sensor."""
        super().__init__(
            conf_name=conf_name,
            coordinator=coordinator,
            entry_id=entry_id,
            description=description,
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "Waarschuwing": self.coordinator.data.get("alarmtxt", None),
        }
