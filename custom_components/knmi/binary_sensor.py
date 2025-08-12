"""Binary sensor platform for knmi."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from weerlive import Response

from .const import DEFAULT_NAME
from .coordinator import KnmiDataUpdateCoordinator
from .entity import KnmiEntity, KnmiEntityDescription


@dataclass(kw_only=True, frozen=True)
class KnmiBinarySensorDescription(KnmiEntityDescription, BinarySensorEntityDescription):
    """Class describing KNMI binary sensor entities."""

    value_fn: Callable[[Response], bool]


DESCRIPTIONS: list[KnmiBinarySensorDescription] = [
    KnmiBinarySensorDescription(
        key="alarm",
        device_class=BinarySensorDeviceClass.SAFETY,
        translation_key="alarm",
        value_fn=lambda data: data.live.alert == 1,
        state_attributes_fn=lambda data: {
            "title": data.live.alert_title,
            "description": data.live.alert_text,
            "code": data.live.weather_code,
            "next_code": data.live.next_alert_weather_code,
            "timestamp": data.live.next_alert_date,
        },
    ),
    KnmiBinarySensorDescription(
        key="sun",
        translation_key="sun",
        value_fn=lambda data: data.live.is_sun_up,
        state_attributes_fn=lambda data: {
            "sunrise": data.live.sunrise,
            "sunset": data.live.sunset,
            "sun_chance0": data.daily_forecast[0].sunshine_probability,
            "sun_chance1": data.daily_forecast[1].sunshine_probability,
            "sun_chance2": data.daily_forecast[2].sunshine_probability,
        },
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[KnmiDataUpdateCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI binary sensors based on a config entry."""
    conf_name = config_entry.data.get(CONF_NAME, hass.config.location_name)
    coordinator = config_entry.runtime_data

    # Add all sensors described above.
    entities: list[KnmiBinarySensor] = [
        KnmiBinarySensor(
            conf_name=conf_name,
            coordinator=coordinator,
            description=description,
        )
        for description in DESCRIPTIONS
    ]

    async_add_entities(entities)


class KnmiBinarySensor(KnmiEntity, BinarySensorEntity):
    """Defines a KNMI binary sensor."""

    entity_description: KnmiBinarySensorDescription

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        description: KnmiBinarySensorDescription,
    ) -> None:
        """Initialize KNMI binary sensor."""
        super().__init__(coordinator=coordinator)

        self._attr_attribution = coordinator.data.api.source
        self._attr_unique_id = f"{DEFAULT_NAME}_{conf_name}_{description.key}".lower()

        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)
