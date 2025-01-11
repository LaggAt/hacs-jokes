"""Config flow for Jokes integration."""
import logging
from typing import Any
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    CONN_CLASS_CLOUD_POLL
)

from .const import (
    CONF_DEVICENAME,
    CONF_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_JOKE_LENGTH,
    CONF_NUM_TRIES,
    DOMAIN,
    DEFAULT_DEVICENAME,
    DEFAULT_NAME,
    DEFAULT_JOKE_LENGTH,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_RETRIES,
)

_LOGGER = logging.getLogger(__name__)

class JokesFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jokes."""

    VERSION = 1.4
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def get_data_schema(self,
                        name: str = None,
                        interval: int | None = None,
                        length: int | None = None,
                        retries: int | None = None,
                        devicename: str | None = None
                        ):
        return vol.Schema({
            vol.Optional(
                CONF_NAME,
                default=name if name else DEFAULT_NAME,
            ): str,
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=interval if interval else DEFAULT_UPDATE_INTERVAL,
                description="Time between fetching new jokes in seconds.",
            ): int,
            vol.Optional(
                CONF_JOKE_LENGTH,
                default=length if length else DEFAULT_JOKE_LENGTH,
                description="Do not allow jokes longer than this.",
            ): int,
            vol.Optional(
                CONF_NUM_TRIES,
                default=retries if retries else DEFAULT_RETRIES,
                description="Number of retries at fetching a joke,",
            ): int,
            vol.Optional(
                CONF_DEVICENAME,
                default=devicename if devicename else DEFAULT_DEVICENAME,
                description="What to call the devices for this integration.",
            ): str,
        })

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show config Form step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=self.get_data_schema(),
            )

        title = f"Random Joke - {user_input[CONF_UPDATE_INTERVAL]}s"
        await self.async_set_unique_id(f"random_joke_{user_input[CONF_UPDATE_INTERVAL]}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=title, data=user_input)
