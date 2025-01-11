"""Provides random jokes."""
from datetime import timedelta
import logging
import asyncio
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_UPDATE_INTERVAL,
    CONF_DEVICENAME,
    CONF_NAME,
    CONF_NUM_TRIES,
    CONF_JOKE_LENGTH,
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_JOKE_LENGTH,
    DEFAULT_DEVICENAME,
    DEFAULT_RETRIES,
)
from .coordinator import JokeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Setup from Config Flow Result."""
    _LOGGER.debug("async_setup_entry")

    hass.data.setdefault(DOMAIN, {})

    coordinator = JokeUpdateCoordinator(
        hass,
        config_entry
    )

    # Perform initial data load from API
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.api_connected:
        raise ConfigEntryNotReady

    # Add listener to enable reconfiguration
    update_listener = config_entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        "coordinator": coordinator,
        "update_listener": update_listener,
    }

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, [Platform.SENSOR])

    return True


async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    # From home assistant developer documentation
    _LOGGER.debug("Migrating configuration from version %s.%s",
                  config_entry.version,
                  config_entry.minor_version
                  )

    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 1:
        new_data = {**config_entry.data}
        if config_entry.minor_version < 1:
            new_data[CONF_NAME] = DEFAULT_NAME
            new_data[CONF_UPDATE_INTERVAL] = DEFAULT_UPDATE_INTERVAL
            new_data[CONF_JOKE_LENGTH] = DEFAULT_JOKE_LENGTH

        if config_entry.minor_version < 3:
            new_data[CONF_DEVICENAME] = DEFAULT_DEVICENAME
            new_data[CONF_NUM_TRIES] = DEFAULT_RETRIES

        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
            minor_version=3,
            version=1
        )

    _LOGGER.debug("Migration to configuration version %s.%s successful",
                  config_entry.version,
                  config_entry.minor_version)

    return True


async def async_remove_config_entry_device(
    _hass: HomeAssistant, _config_entry: ConfigEntry, _device_entry: DeviceEntry
) -> bool:
    """Delete device if selected from UI."""
    # Adding this function shows the delete device option in the UI.
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when you remove your integration or shutdown HA.

    # Remove the config options update listener
    hass.data[DOMAIN][config_entry.entry_id]["update_listener"]()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, Platform.SENSOR
    )

    # Remove the config entry from the hass data object.
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
