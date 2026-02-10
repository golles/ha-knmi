"""Adds config flow for knmi."""

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import SOURCE_RECONFIGURE, ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from weerlive import WeerliveApi, WeerliveAPIConnectionError, WeerliveAPIKeyError, WeerliveAPIRateLimitError

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Required(CONF_API_KEY): str,
    }
)


class KnmiFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for knmi."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        user_input = user_input or {}

        if user_input:
            name = user_input[CONF_NAME]
            api_key = user_input[CONF_API_KEY]
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]

            try:
                await self._validate_user_input(
                    api_key,
                    latitude,
                    longitude,
                )
            except WeerliveAPIConnectionError:
                errors["base"] = "general"
            except WeerliveAPIKeyError:
                errors["base"] = "api_key"
            except WeerliveAPIRateLimitError:
                errors["base"] = "daily_limit"
            else:
                if self.source == SOURCE_RECONFIGURE:
                    return self.async_update_reload_and_abort(
                        self._get_reconfigure_entry(),
                        title=name,
                        data=user_input,
                    )
                return self.async_create_entry(
                    title=name,
                    data=user_input,
                )

        default_data = {
            CONF_NAME: self.hass.config.location_name,
            CONF_LATITUDE: self.hass.config.latitude,
            CONF_LONGITUDE: self.hass.config.longitude,
        }
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(CONFIG_SCHEMA, default_data),
            description_placeholders={
                "weerlive_url": "https://weerlive.nl/delen.php",
            },
            errors=errors,
        )

    async def _validate_user_input(self, api_key: str, latitude: float, longitude: float) -> None:
        """Validate user input."""
        session = async_get_clientsession(self.hass)
        client = WeerliveApi(api_key, session)
        await client.latitude_longitude(latitude, longitude)

    async def async_step_reconfigure(self, _: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reconfiguration."""
        data = self._get_reconfigure_entry().data.copy()

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(CONFIG_SCHEMA, data),
        )

    @staticmethod
    @callback
    def async_get_options_flow(_config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return KnmiOptionsFlowHandler()


class KnmiOptionsFlowHandler(OptionsFlow):
    """Knmi config flow options handler."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title=self.config_entry.data.get(CONF_NAME), data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=300, max=86400))
                }
            ),
        )
