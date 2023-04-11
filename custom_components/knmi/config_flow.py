"""Adds config flow for knmi."""
import logging

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .api import (
    KnmiApiClient,
    KnmiApiClientApiKeyError,
    KnmiApiClientCommunicationError,
    KnmiApiRateLimitError,
)
from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class KnmiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for knmi."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._validate_user_input(
                    user_input[CONF_API_KEY],
                    user_input[CONF_LATITUDE],
                    user_input[CONF_LONGITUDE],
                )
            except KnmiApiClientCommunicationError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "general"
            except KnmiApiClientApiKeyError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "api_key"
            except KnmiApiRateLimitError as exception:
                _LOGGER.error(exception)
                _errors["base"] = "daily_limit"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Required(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=_errors,
        )

    async def _validate_user_input(self, api_key: str, latitude: str, longitude: str):
        """Validate user input."""
        session = async_create_clientsession(self.hass)
        client = KnmiApiClient(api_key, latitude, longitude, session)
        await client.async_get_data()
