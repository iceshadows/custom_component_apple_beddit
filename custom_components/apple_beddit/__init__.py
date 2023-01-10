"""The Apple Beddit integration."""
from __future__ import annotations

import logging

from bleak import BleakClient

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import *
from .coordinator import *
from .device import *

_LOGGER: logging.Logger = logging.getLogger(__package__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Apple Beddit from a config entry."""

    address = entry.data["mac"]
    _LOGGER.error(entry.data["mac"])
    discoverable = bluetooth.async_address_present(hass, address, connectable=True)
    if discoverable:
        ble_devcie = bluetooth.async_ble_device_from_address(hass, address=address)
        bleak_c = BleakClient(ble_devcie)
        device = AppleBedditMointor(ble_devcie.address, ble_devcie.name, bleak_c)
        coordinator = hass.data.setdefault(DOMAIN, {})[
            entry.entry_id
        ] = AppleBedditDataUpdateCoordinator(
            hass, device, entry.options.get(OPTION_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        # fetch the data
        await coordinator.async_refresh()
        if not coordinator.last_update_success:
            raise ConfigEntryNotReady

        # store the coordinator so to be accessible by each platform
        hass.data[DOMAIN][entry.entry_id] = coordinator
        for platform in PLATFORMS:
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )
        entry.add_update_listener(async_reload_entry)
        _LOGGER.error("Loaded entry %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    bluetooth.async_rediscover_address(hass, entry.data["mac"])
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
