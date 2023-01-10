import logging

from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import Config, HomeAssistant

from .const import DOMAIN
from .device import AppleBedditMointor

_LOGGER: logging.Logger = logging.getLogger(__package__)


class AppleBedditEntity(CoordinatorEntity):
    """imou entity class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        sensor_instance,
        entity_format,
        hass: HomeAssistant,
    ):
        """Initialize."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.hass = hass
        self.device: AppleBedditMointor = coordinator.device
        self.sensor_instance = sensor_instance
        self.entity_id = async_generate_entity_id(
            entity_format,
            f"{self.device.get_name()}_{self.sensor_instance['name']}",
            hass=coordinator.hass,
        )

    @property
    def id(self):
        """Return ID to use for this entity."""
        return self.sensor_instance["id"]

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "_" + self.sensor_instance["name"]

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": self.device.get_name(),
            "model": "apple.beddit",
            "manufacturer": "Apple Inc.",
        }

    @property
    def available(self) -> bool:
        """Device available."""
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.device.get_name()} {self.sensor_instance['name']}"

    @property
    def icon(self):
        """Return the icon of this sensor."""
        return "mdi:bookmark"

    async def async_added_to_hass(self):
        """Entity added to HA (at startup or when re-enabled)."""
        await super().async_added_to_hass()
        _LOGGER.error("%s added to HA", self.name)
        # self.sensor_instance.set_enabled(True)
        # request an update of this sensor

    async def async_will_remove_from_hass(self):
        """Entity removed from HA (when disabled)."""
        await super().async_added_to_hass()
        _LOGGER.error("%s removed from HA", self.name)
