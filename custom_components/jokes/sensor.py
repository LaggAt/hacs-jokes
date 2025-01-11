"""Joke Sensor."""
import logging

from homeassistant.core import callback, HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_STATE_JOKE_LENGTH, CONF_UPDATE_INTERVAL
from .coordinator import JokeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
):
    """Setup the sensors."""
    coordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    async_add_entities([JokeEntity(coordinator, coordinator.data)])


class JokeEntity(CoordinatorEntity, SensorEntity):
    """Dummy entity to trigger updates."""

    _attr_icon = "mdi:emoticon-excited-outline"

    def __init__(self, coordinator: JokeUpdateCoordinator, device):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        self.device = device
        self.device_id = device["id"]


    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.data
        _LOGGER.debug("Device: %s", self.device)
        self.async_write_ha_state()


    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            name=f"Random Joke - {self.coordinator.update_interval}",
            manufacturer="LaggAt",
            model="Random Joke",
            sw_version="0.0.1",
            identifiers={
                (
                    DOMAIN,
                    f"{self.device_id}",
                )
            },
        )


    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device["name"]


    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return f"{DOMAIN}-{self.device['uid']}"


    @property
    def state(self):
        """Return the state of the sensor."""
        # Cut off joke at joke_length chars... Full joke exists in extra attributes
        cutoff = min(MAX_STATE_JOKE_LENGTH, self.coordinator.joke_length)
        return self.device["state"]["joke"][:cutoff]


    @property
    def extra_state_attributes(self):
        """Return the extra attributes and full state of the sensor."""
        return self.device["state"]
