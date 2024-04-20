"""Binary sensor platform for knmi."""

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import KnmiDataUpdateCoordinator
from .sensor import KnmiSensorDescription

DESCRIPTIONS: list[KnmiSensorDescription] = [
    KnmiSensorDescription(
        key="alarm",
        device_class=BinarySensorDeviceClass.SAFETY,
        translation_key="alarm",
        value_fn=lambda coordinator: coordinator.get_value(["liveweer", 0, "alarm"])
        == 1,
        attr_fn=lambda coordinator: {
            "title": coordinator.get_value(["liveweer", 0, "lkop"]),
            "description": coordinator.get_value(["liveweer", 0, "ltekst"]),
            "code": coordinator.get_value(["liveweer", 0, "wrschklr"]),
            "next_code": coordinator.get_value(["liveweer", 0, "wrsch_gc"]),
            "timestamp": coordinator.get_value_datetime(
                ["liveweer", 0, "wrsch_gts"], "-"
            ),
        },
    ),
    KnmiSensorDescription(
        key="sun",
        translation_key="sun",
        value_fn=lambda coordinator: coordinator.get_is_sun_up(),
        attr_fn=lambda coordinator: {
            "sunrise": coordinator.get_value_datetime(["liveweer", 0, "sup"]),
            "sunset": coordinator.get_value_datetime(["liveweer", 0, "sunder"]),
            "sun_chance0": coordinator.get_value(["wk_verw", 0, "zond_perc_dag"]),
            "sun_chance1": coordinator.get_value(["wk_verw", 1, "zond_perc_dag"]),
            "sun_chance2": coordinator.get_value(["wk_verw", 2, "zond_perc_dag"]),
        },
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI binary sensors based on a config entry."""
    conf_name = entry.data.get(CONF_NAME, hass.config.location_name)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[KnmiBinarySensor] = []

    # Add all sensors described above.
    for description in DESCRIPTIONS:
        entities.append(
            KnmiBinarySensor(
                conf_name=conf_name,
                coordinator=coordinator,
                description=description,
            )
        )

    async_add_entities(entities)


class KnmiBinarySensor(
    CoordinatorEntity[KnmiDataUpdateCoordinator], BinarySensorEntity
):
    """Defines a KNMI binary sensor."""

    _attr_has_entity_name = True
    entity_description: KnmiSensorDescription

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize KNMI binary sensor."""
        super().__init__(coordinator=coordinator)

        self._attr_attribution = self.coordinator.get_value(["api", 0, "bron"])
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{DEFAULT_NAME}_{conf_name}_{description.key}".lower()

        self.entity_description = description

    @property
    def is_on(self) -> StateType:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self.entity_description.attr_fn(self.coordinator)
