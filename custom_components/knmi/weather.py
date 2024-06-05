"""Weather platform for knmi."""

import logging

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    DOMAIN as SENSOR_DOMAIN,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import KnmiDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Map weather conditions from KNMI to HA.
CONDITIONS_MAP = {
    "zonnig": ATTR_CONDITION_SUNNY,
    "bliksem": ATTR_CONDITION_LIGHTNING,
    "regen": ATTR_CONDITION_POURING,
    "buien": ATTR_CONDITION_RAINY,
    "hagel": ATTR_CONDITION_HAIL,
    "mist": ATTR_CONDITION_FOG,
    "sneeuw": ATTR_CONDITION_SNOWY,
    "bewolkt": ATTR_CONDITION_CLOUDY,
    "lichtbewolkt": ATTR_CONDITION_PARTLYCLOUDY,
    "halfbewolkt": ATTR_CONDITION_PARTLYCLOUDY,
    "halfbewolkt_regen": ATTR_CONDITION_RAINY,
    "zwaarbewolkt": ATTR_CONDITION_CLOUDY,
    "nachtmist": ATTR_CONDITION_FOG,
    "helderenacht": ATTR_CONDITION_CLEAR_NIGHT,
    "nachtbewolkt": ATTR_CONDITION_CLOUDY,
    # TODO: Check with the supplier why this is still in the response while not in the docs.
    "wolkennacht": ATTR_CONDITION_CLOUDY,
    # Possible unavailable conditions.
    "-": None,
    "_": None,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI weather based on a config entry."""
    async_add_entities(
        [
            KnmiWeather(
                conf_name=entry.data.get(CONF_NAME, hass.config.location_name),
                coordinator=hass.data[DOMAIN][entry.entry_id],
            )
        ]
    )


class KnmiWeather(WeatherEntity):
    """Defines a KNMI weather entity."""

    _attr_has_entity_name = True
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_visibility_unit = UnitOfLength.METERS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
    ):
        self.coordinator = coordinator

        self._attr_name = conf_name
        self._attr_attribution = self.coordinator.get_value(["api", 0, "bron"])
        self._attr_unique_id = f"{DEFAULT_NAME}_{conf_name}".lower()
        self._attr_device_info = self.coordinator.device_info
        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{conf_name}".lower()

    def map_condition(self, value: str | None) -> str | None:
        """Map weather conditions from KNMI to HA."""

        try:
            return CONDITIONS_MAP[value]
        except KeyError:
            _LOGGER.error(
                'Weather condition "%s" can\'t be mapped, please raise a bug', value
            )
        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        condition = self.map_condition(
            self.coordinator.get_value(["liveweer", 0, "image"])
        )

        if condition == ATTR_CONDITION_SUNNY and not self.coordinator.get_is_sun_up():
            condition = ATTR_CONDITION_CLEAR_NIGHT

        if condition == ATTR_CONDITION_SNOWY and self.native_temperature > 6:
            condition = ATTR_CONDITION_RAINY

        return condition

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature in native units."""
        return self.coordinator.get_value(["liveweer", 0, "temp"])

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature in native units."""
        return self.coordinator.get_value(["liveweer", 0, "gtemp"])

    @property
    def native_dew_point(self) -> float | None:
        """Return the dew point temperature in native units."""
        return self.coordinator.get_value(["liveweer", 0, "dauwp"])

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure in native units."""
        return self.coordinator.get_value(["liveweer", 0, "luchtd"])

    @property
    def humidity(self) -> float | None:
        """Return the humidity in native units."""
        return self.coordinator.get_value(["liveweer", 0, "lv"])

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed in native units."""
        return self.coordinator.get_value(["liveweer", 0, "windkmh"])

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        return self.coordinator.get_value(["liveweer", 0, "windrgr"])

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility in native units."""
        return self.coordinator.get_value(["liveweer", 0, "zicht"])

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        forecasts = []

        for i in range(len(self.coordinator.get_value(["wk_verw"]))):
            time = self.coordinator.get_value_datetime(["wk_verw", i, "dag"])

            forecast = {
                ATTR_FORECAST_TIME: time.isoformat() if time else None,
                ATTR_FORECAST_CONDITION: self.map_condition(
                    self.coordinator.get_value(["wk_verw", i, "image"])
                ),
                ATTR_FORECAST_TEMP_LOW: self.coordinator.get_value(
                    ["wk_verw", i, "min_temp"]
                ),
                ATTR_FORECAST_TEMP: self.coordinator.get_value(
                    ["wk_verw", i, "max_temp"]
                ),
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: self.coordinator.get_value(
                    ["wk_verw", i, "neersl_perc_dag"]  # Percentage.
                ),
                ATTR_FORECAST_WIND_BEARING: self.coordinator.get_value(
                    ["wk_verw", i, "windrgr"]
                ),
                ATTR_FORECAST_WIND_SPEED: self.coordinator.get_value(
                    ["wk_verw", i, "windkmh"]
                ),
                # Not officially supported, but nice additions.
                "wind_speed_bft": self.coordinator.get_value(["wk_verw", i, "windbft"]),
                "sun_chance": self.coordinator.get_value(
                    ["wk_verw", i, "zond_perc_dag"]
                ),
            }
            forecasts.append(forecast)

        return forecasts

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        forecasts = []

        for i in range(len(self.coordinator.get_value(["uur_verw"]))):
            time = self.coordinator.get_value_datetime(["uur_verw", i, "uur"])

            forecast = {
                ATTR_FORECAST_TIME: time.isoformat() if time else None,
                ATTR_FORECAST_CONDITION: self.map_condition(
                    self.coordinator.get_value(["uur_verw", i, "image"])
                ),
                ATTR_FORECAST_TEMP: self.coordinator.get_value(["uur_verw", i, "temp"]),
                ATTR_FORECAST_PRECIPITATION: self.coordinator.get_value(
                    ["uur_verw", i, "neersl"]  # Millimeter.
                ),
                ATTR_FORECAST_WIND_BEARING: self.coordinator.get_value(
                    ["uur_verw", i, "windrgr"]
                ),
                ATTR_FORECAST_WIND_SPEED: self.coordinator.get_value(
                    ["uur_verw", i, "windkmh"]
                ),
                # Not officially supported, but nice additions.
                "wind_speed_bft": self.coordinator.get_value(
                    ["uur_verw", i, "windbft"]
                ),
                "solar_irradiance": self.coordinator.get_value(["uur_verw", i, "gr"]),
            }
            forecasts.append(forecast)

        return forecasts

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        raise NotImplementedError
