"""Sensor platform for knmi."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    PERCENTAGE,
    UnitOfIrradiance,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import KnmiDataUpdateCoordinator


@dataclass(kw_only=True, frozen=True)
class KnmiSensorDescription(SensorEntityDescription):
    """Class describing KNMI sensor entities."""

    value_fn: Callable[[dict[str, Any]], StateType | datetime | None]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] = lambda _: {}


DESCRIPTIONS: list[KnmiSensorDescription] = [
    KnmiSensorDescription(
        key="dauwp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="dauwp",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "dauwp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="gr",
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="gr",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "gr"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="gtemp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="gtemp",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "gtemp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="luchtd",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="luchtd",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "luchtd"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="lv",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="lv",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "lv"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="max_temp_today",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="max_temp_today",
        value_fn=lambda coordinator: coordinator.get_value(["wk_verw", 0, "max_temp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="max_temp_tomorrow",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="max_temp_tomorrow",
        value_fn=lambda coordinator: coordinator.get_value(["wk_verw", 1, "max_temp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="min_temp_today",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="min_temp_today",
        value_fn=lambda coordinator: coordinator.get_value(["wk_verw", 0, "min_temp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="min_temp_tomorrow",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="min_temp_tomorrow",
        value_fn=lambda coordinator: coordinator.get_value(["wk_verw", 1, "min_temp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="neersl_perc_dag_today",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="neersl_perc_dag_today",
        value_fn=lambda coordinator: coordinator.get_value(
            ["wk_verw", 0, "neersl_perc_dag"]
        ),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="neersl_perc_dag_tomorrow",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="neersl_perc_dag_tomorrow",
        value_fn=lambda coordinator: coordinator.get_value(
            ["wk_verw", 1, "neersl_perc_dag"]
        ),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="plaats",
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="plaats",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "plaats"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="rest_verz",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="rest_verz",
        value_fn=lambda coordinator: coordinator.get_value(["api", 0, "rest_verz"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="samenv",
        translation_key="samenv",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "samenv"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="temp",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "temp"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="timestamp",
        value_fn=lambda coordinator: coordinator.get_value_datetime(
            ["liveweer", 0, "timestamp"]
        ),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="verw",
        translation_key="verw",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "verw"]),
    ),
    KnmiSensorDescription(
        key="windkmh",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="windkmh",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "windkmh"]),
        attr_fn=lambda coordinator: {
            "bearing": coordinator.get_value(["liveweer", 0, "windr"]),
            "degree": coordinator.get_value(["liveweer", 0, "windrgr"]),
            "beaufort": coordinator.get_value(["liveweer", 0, "windbft"]),
            "knots": coordinator.get_value(["liveweer", 0, "windknp"]),
        },
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="wrschklr",
        translation_key="wrschklr",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "wrschklr"]),
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="zicht",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="zicht",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "zicht"]),
        entity_registry_enabled_default=False,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI sensors based on a config entry."""
    conf_name = entry.data.get(CONF_NAME, hass.config.location_name)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[KnmiSensor] = []

    # Add all sensors described above.
    for description in DESCRIPTIONS:
        entities.append(
            KnmiSensor(
                conf_name=conf_name,
                coordinator=coordinator,
                description=description,
            )
        )

    async_add_entities(entities)


class KnmiSensor(CoordinatorEntity[KnmiDataUpdateCoordinator], SensorEntity):
    """Defines a KNMI sensor."""

    _attr_has_entity_name = True
    entity_description: KnmiSensorDescription

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize KNMI sensor."""
        super().__init__(coordinator=coordinator)

        self._attr_attribution = self.coordinator.get_value(["api", 0, "bron"])
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{DEFAULT_NAME}_{conf_name}_{description.key}".lower()

        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self.entity_description.attr_fn(self.coordinator)
