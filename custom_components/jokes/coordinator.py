"""Provides the coordinator for the joke integration."""
import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import (
    CONF_DEVICENAME,
    CONF_NAME,
    CONF_JOKE_LENGTH,
    CONF_UPDATE_INTERVAL,
    CONF_NUM_TRIES,
    DEFAULT_NAME,
    DEFAULT_JOKE_LENGTH,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_RETRIES,
    DOMAIN,
    MIN_UPDATE_INTERVAL,
    MIN_RETRIES,
)

HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Jokes custom integration for Home Assistant (https://github.com/LaggAt/ha-jokes)'
}

_LOGGER = logging.getLogger(__name__)

class JokeUpdateCoordinator(DataUpdateCoordinator):
    """Update handler."""

    def __init__(self, hass, config_entry):
        """Initialize global data updater."""
        _LOGGER.debug("__init__")

        self.api_connected = False

        self.device_friendly_name = config_entry.data.get(
            CONF_NAME,
            DEFAULT_NAME
        )

        self.joke_length = config_entry.data.get(
            CONF_JOKE_LENGTH,
            DEFAULT_JOKE_LENGTH
        )

        self.uid = config_entry.unique_id
        # Get the update interval and ensure that it is not too small
        self.update_interval = timedelta(
            seconds=max(
                config_entry.data.get(
                    CONF_UPDATE_INTERVAL,
                    DEFAULT_UPDATE_INTERVAL
                ),
                MIN_UPDATE_INTERVAL
            )
        )

        self.retries = max(
            config_entry.data.get(
                CONF_NUM_TRIES,
                DEFAULT_RETRIES
            ),
            MIN_RETRIES
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({self.uid})",
            update_interval=self.update_interval,
            update_method=self._async_update_data,
        )


    async def _async_update_data(self):
        """Fetch a random joke."""
        _LOGGER.debug("_async_update_data")

        try:
            device = {
                "id": f"{self.uid}",
                "uid": f"{self.uid}_device",
                "name": self.device_friendly_name,
                "state": await self._async_get_data(),
            }

        except Exception as err:
            _LOGGER.error(err)
            raise UpdateFailed from err

        return device


    async def _async_get_data(self):
        async with aiohttp.ClientSession() as session:
            for _ in range(0, self.retries):
                async with session.get(
                        'https://icanhazdadjoke.com/',
                        headers=HEADERS
                ) as resp:
                    if resp.status == 200:
                        json = await resp.json()

                        # Ensure that joke exists and is not too long
                        if "joke" not in json or len(json["joke"]) > self.joke_length:
                            continue

                        # Signal that we got a connection,
                        # so we know that the integration should not give up
                        self.api_connected = True
                        return json
                    raise UpdateFailed(f"Response status code: {resp.status}")
        raise UpdateFailed(f"Could not get joke after {self.retries} tries")
