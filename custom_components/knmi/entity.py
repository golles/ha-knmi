"""KNMI entity."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from weerlive import Response

from .const import DOMAIN
from .coordinator import KnmiDataUpdateCoordinator


@dataclass(kw_only=True, frozen=True)
class KnmiEntityDescription(EntityDescription):
    """Class describing KNMI entities."""

    state_attributes_fn: Callable[[Response], dict[str, Any]] = lambda _: {}


class KnmiEntity(CoordinatorEntity[KnmiDataUpdateCoordinator]):
    """Representation of a KNMI entity."""

    entity_description: KnmiEntityDescription

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KnmiDataUpdateCoordinator,
    ) -> None:
        """Initialize the KNMI entity."""
        super().__init__(coordinator=coordinator)

        self.coordinator = coordinator

        self._attr_device_info = DeviceInfo(
            configuration_url="https://weerlive.nl/api/toegang/account.php",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer="Weerlive",
            name=coordinator.config_entry.data.get(CONF_NAME),
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return self.entity_description.state_attributes_fn(self.coordinator.data)
