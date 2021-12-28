"""KnmiEntity class"""
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION, ATTRIBUTION


class KnmiEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry

    def getData(self, key):
        """Return the data key from the coordinator."""
        if self.coordinator.data is not None:
            return self.coordinator.data[key]
        return None

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.name}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": NAME,
            "model": VERSION,
            "manufacturer": NAME,
            "entry_type": DeviceEntryType.SERVICE,
            "configuration_url": "http://weerlive.nl/api/toegang/account.php",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "integration": DOMAIN,
        }
