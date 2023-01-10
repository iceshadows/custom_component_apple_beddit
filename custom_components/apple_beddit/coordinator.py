"""Class to manage fetching data from the API."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .device import AppleBedditMointor

_LOGGER: logging.Logger = logging.getLogger(__package__)


class AppleBedditDataUpdateCoordinator(DataUpdateCoordinator):
    """Implement the DataUpdateCoordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: AppleBedditMointor,
        scan_interval: int,
    ) -> None:
        """Initialize."""
        self.scan_inteval = scan_interval
        self.device = device
        self.platforms = []
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.scan_inteval),
        )
        _LOGGER.error(
            "Initialized coordinator. Scan internal %d seconds", self.scan_inteval
        )

    async def _async_update_data(self):
        """HA calls this every DEFAULT_SCAN_INTERVAL to run the update."""
        try:
            if not self.device.inited:
                _LOGGER.error("initing device")
                await self.device.connect()
                return False
            if not self.device.available:
                _LOGGER.error("retrying connect device")
                await self.device.connect()
                return False
            sensors = self.device.sensors_data
            for s_i in self.device.sensor_instances:
                s_i.set_state(sensors[s_i.sensor_id]["state"])

            return True
        except Exception as exception:
            _LOGGER.error(exception)
            raise UpdateFailed() from exception
