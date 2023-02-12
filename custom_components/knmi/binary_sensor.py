"""Binary sensor platform for knmi."""

from collections.abc import Mapping
import datetime
from typing import Any

from homeassistant.components.binary_sensor import (
    DOMAIN as SENSOR_DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt
import pytz

from . import KnmiDataUpdateCoordinator
from .const import API_TIMEZONE, DEFAULT_NAME, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI binary sensors based on a config entry."""
    conf_name = entry.data.get(CONF_NAME, hass.config.location_name)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            KnmiBinaryAlarmSensor(
                conf_name=conf_name,
                coordinator=coordinator,
                entry_id=entry.entry_id,
                description=SensorEntityDescription(
                    key="alarm",
                    name="Waarschuwing",
                    icon="mdi:alert",
                    device_class=BinarySensorDeviceClass.SAFETY,
                ),
            ),
            KnmiBinarySunSensor(
                conf_name=conf_name,
                coordinator=coordinator,
                entry_id=entry.entry_id,
                description=SensorEntityDescription(
                    key="sun",
                    name="Zon",
                    icon="mdi:white-balance-sunny",
                ),
            ),
        ]
    )


class KnmiBinarySensor(
    CoordinatorEntity[KnmiDataUpdateCoordinator], BinarySensorEntity
):
    """Defines a KNMI binary sensor."""

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
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {conf_name} {self.name}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the entity is on."""
        raise NotImplementedError("Update method not implemented")


class KnmiBinaryAlarmSensor(KnmiBinarySensor):
    """Defines a KNMI alarm binary sensor."""

    @property
    def is_on(self) -> bool:
        """Return True if the entity is on."""
        value = self.coordinator.get_value(self.entity_description.key, int)

        if value is not None:
            return value != 0
        return None

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "Waarschuwing": self.coordinator.get_value("alarmtxt"),
        }


class KnmiBinarySunSensor(KnmiBinarySensor):
    """Defines a KNMI sun binary sensor."""

    @property
    def is_on(self) -> bool:
        """Return True if the entity is on."""
        sup = self.coordinator.get_value("sup")
        sunder = self.coordinator.get_value("sunder")

        if sup is None or sunder is None:
            return None

        sunrise = self.time_as_datetime(sup)
        sunset = self.time_as_datetime(sunder)

        now = dt.utcnow()

        if sunrise < now < sunset:
            return True
        return False

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        sup = self.coordinator.get_value("sup")
        sunder = self.coordinator.get_value("sunder")
        d0zon = self.coordinator.get_value("d0zon")
        d1zon = self.coordinator.get_value("d1zon")
        d2zon = self.coordinator.get_value("d2zon")

        return {
            "Zonsopkomst": (
                self.time_as_datetime(sup).isoformat() if sup is not None else None
            ),
            "Zonondergang": (
                self.time_as_datetime(sunder).isoformat() if sup is not None else None
            ),
            "Zonkans vandaag": (d0zon if d0zon is not None else None),
            "Zonkans morgen": (d1zon if d1zon is not None else None),
            "Zonkans overmorgen": (d2zon if d2zon is not None else None),
        }

    @classmethod
    def time_as_datetime(cls, time: str) -> datetime.datetime:
        """
        Parse a time from a string like "08:13" to a datetime.
        The returned datetime is in UTC, using today as the date.
        """
        time_array = time.split(":")
        timezone = pytz.timezone(API_TIMEZONE)
        now = dt.now(timezone)
        time = now.replace(
            hour=int(time_array[0]), minute=int(time_array[1]), second=0, microsecond=0
        )

        return dt.as_utc(time)
