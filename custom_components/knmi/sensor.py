"""Sensor platform for knmi."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, UnitOfIrradiance, UnitOfLength, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from weerlive import Response

from .const import DEFAULT_NAME
from .coordinator import KnmiDataUpdateCoordinator
from .entity import KnmiEntity, KnmiEntityDescription


@dataclass(kw_only=True, frozen=True)
class KnmiSensorDescription(KnmiEntityDescription, SensorEntityDescription):
    """Class describing KNMI sensor entities."""

    value_fn: Callable[[Response], StateType | datetime | None]


DESCRIPTIONS: list[KnmiSensorDescription] = [
    KnmiSensorDescription(
        key="dauwp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="dauwp",
        value_fn=lambda data: data.live.dew_point,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="gr",
        native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
        device_class=SensorDeviceClass.IRRADIANCE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="gr",
        value_fn=lambda data: data.live.solar_irradiance,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="gtemp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="gtemp",
        value_fn=lambda data: data.live.feels_like_temperature,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="luchtd",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="luchtd",
        value_fn=lambda data: data.live.air_pressure,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="lv",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="lv",
        value_fn=lambda data: data.live.humidity,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="max_temp_today",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="max_temp_today",
        value_fn=lambda data: data.daily_forecast[0].max_temperature,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="max_temp_tomorrow",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="max_temp_tomorrow",
        value_fn=lambda data: data.daily_forecast[1].max_temperature,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="min_temp_today",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="min_temp_today",
        value_fn=lambda data: data.daily_forecast[0].min_temperature,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="min_temp_tomorrow",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="min_temp_tomorrow",
        value_fn=lambda data: data.daily_forecast[1].min_temperature,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="neersl_perc_dag_today",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="neersl_perc_dag_today",
        value_fn=lambda data: data.daily_forecast[0].precipitation_probability,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="neersl_perc_dag_tomorrow",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="neersl_perc_dag_tomorrow",
        value_fn=lambda data: data.daily_forecast[1].precipitation_probability,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="plaats",
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="plaats",
        value_fn=lambda data: data.live.city,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="rest_verz",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="rest_verz",
        value_fn=lambda data: data.api.remaining_requests,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="samenv",
        translation_key="samenv",
        value_fn=lambda data: data.live.summary,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="temp",
        value_fn=lambda data: data.live.temperature,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="timestamp",
        value_fn=lambda data: data.live.time,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="verw",
        translation_key="verw",
        value_fn=lambda data: data.live.forecast,
    ),
    KnmiSensorDescription(
        key="windkmh",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="windkmh",
        value_fn=lambda data: data.live.wind_speed_kmh,
        state_attributes_fn=lambda data: {
            "bearing": data.live.wind_direction,
            "degree": data.live.wind_direction_degree,
            "beaufort": data.live.wind_speed_bft,
            "knots": data.live.wind_speed_knots,
        },
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="wrschklr",
        translation_key="wrschklr",
        value_fn=lambda data: data.live.weather_code,
        entity_registry_enabled_default=False,
    ),
    KnmiSensorDescription(
        key="zicht",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="zicht",
        value_fn=lambda data: data.live.visibility,
        entity_registry_enabled_default=False,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[KnmiDataUpdateCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI sensors based on a config entry."""
    conf_name = config_entry.data.get(CONF_NAME, hass.config.location_name)
    coordinator = config_entry.runtime_data

    # Add all sensors described above.
    entities: list[KnmiSensor] = [
        KnmiSensor(
            conf_name=conf_name,
            coordinator=coordinator,
            description=description,
        )
        for description in DESCRIPTIONS
    ]

    async_add_entities(entities)


class KnmiSensor(KnmiEntity, SensorEntity):
    """Defines a KNMI sensor."""

    entity_description: KnmiSensorDescription

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        description: KnmiSensorDescription,
    ) -> None:
        """Initialize KNMI sensor."""
        super().__init__(coordinator=coordinator)

        self._attr_attribution = self.coordinator.data.api.source
        self._attr_unique_id = f"{DEFAULT_NAME}_{conf_name}_{description.key}".lower()

        self.entity_description = description

    @property
    def native_value(self) -> StateType | datetime | None:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator.data)
