"""Weather platform for knmi."""

import logging
from dataclasses import dataclass

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
    Forecast,
    WeatherEntity,
    WeatherEntityDescription,
    WeatherEntityFeature,
)
from homeassistant.components.weather import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, UnitOfLength, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_NAME
from .coordinator import KnmiDataUpdateCoordinator
from .entity import KnmiEntity, KnmiEntityDescription

_LOGGER: logging.Logger = logging.getLogger(__package__)

SNOW_TO_RAIN_TEMP_CELSIUS = 6


@dataclass(kw_only=True, frozen=True)
class KnmiWeatherDescription(KnmiEntityDescription, WeatherEntityDescription):
    """Class describing KNMI weather entities."""


DESCRIPTIONS: list[KnmiWeatherDescription] = [
    KnmiWeatherDescription(
        key="weer",
    ),
]

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
    # Check with the supplier why this is still in the response while not in the docs.
    "wolkennacht": ATTR_CONDITION_CLOUDY,
    # Possible unavailable conditions.
    "-": None,
    "_": None,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[KnmiDataUpdateCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNMI weather based on a config entry."""
    conf_name = config_entry.data.get(CONF_NAME, hass.config.location_name)
    coordinator = config_entry.runtime_data

    # Add all sensors described above.
    entities: list[KnmiWeather] = [
        KnmiWeather(
            conf_name=conf_name,
            coordinator=coordinator,
            description=description,
        )
        for description in DESCRIPTIONS
    ]

    async_add_entities(entities)


class KnmiWeather(KnmiEntity, WeatherEntity):
    """Defines a KNMI weather entity."""

    entity_description: KnmiWeatherDescription

    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_visibility_unit = UnitOfLength.METERS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        description: KnmiWeatherDescription,
    ) -> None:
        """Initialize KNMI weather entity."""
        super().__init__(coordinator=coordinator)

        self._attr_attribution = self.coordinator.data.api.source
        self._attr_unique_id = f"{DEFAULT_NAME}_{conf_name}".lower()

        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{conf_name}".lower()
        self.entity_description = description

    def map_condition(self, value: str | None) -> str | None:
        """Map weather conditions from KNMI to HA."""
        try:
            return CONDITIONS_MAP[value]  # type: ignore  # noqa: PGH003
        except KeyError:
            _LOGGER.exception('Weather condition "%s" can\'t be mapped, please raise a bug', value)
        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        condition = self.map_condition(self.coordinator.data.live.image)

        if condition == ATTR_CONDITION_SUNNY and not self.coordinator.data.live.is_sun_up:
            condition = ATTR_CONDITION_CLEAR_NIGHT

        if condition == ATTR_CONDITION_SNOWY and self.native_temperature and self.native_temperature > SNOW_TO_RAIN_TEMP_CELSIUS:
            condition = ATTR_CONDITION_RAINY

        return condition

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature in native units."""
        return self.coordinator.data.live.temperature

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature in native units."""
        return self.coordinator.data.live.feels_like_temperature

    @property
    def native_dew_point(self) -> float | None:
        """Return the dew point temperature in native units."""
        return self.coordinator.data.live.dew_point

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure in native units."""
        return self.coordinator.data.live.air_pressure

    @property
    def humidity(self) -> float | None:
        """Return the humidity in native units."""
        return self.coordinator.data.live.humidity

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed in native units."""
        return self.coordinator.data.live.wind_speed_kmh

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        return self.coordinator.data.live.wind_direction_degree

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility in native units."""
        return self.coordinator.data.live.visibility

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        forecasts: list[Forecast] = []

        for daily_forecast in self.coordinator.data.daily_forecast:
            forecast = Forecast(
                condition=self.map_condition(daily_forecast.image),
                datetime=daily_forecast.day.isoformat(),
                precipitation_probability=daily_forecast.precipitation_probability,  # Note: Percentage.
                native_temperature=daily_forecast.max_temperature,
                native_templow=daily_forecast.min_temperature,
                wind_bearing=daily_forecast.wind_direction_degree,
                native_wind_speed=daily_forecast.wind_speed_kmh,
            )

            # Not officially supported, but nice additions.
            forecast["wind_speed_bft"] = daily_forecast.wind_speed_bft  # type: ignore # noqa: PGH003
            forecast["sun_chance"] = daily_forecast.sunshine_probability  # type: ignore # noqa: PGH003

            forecasts.append(forecast)

        return forecasts

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        forecasts: list[Forecast] = []

        for hourly_forecast in self.coordinator.data.hourly_forecast:
            forecast = Forecast(
                condition=self.map_condition(hourly_forecast.image),
                datetime=hourly_forecast.time.isoformat(),
                native_precipitation=hourly_forecast.precipitation,  # Millimeter.
                native_temperature=hourly_forecast.temperature,
                wind_bearing=hourly_forecast.wind_direction_degree,
                native_wind_speed=hourly_forecast.wind_speed_kmh,
            )

            # Not officially supported, but nice additions.
            forecast["wind_speed_bft"] = hourly_forecast.wind_speed_bft  # type: ignore # noqa: PGH003
            forecast["solar_irradiance"] = hourly_forecast.solar_irradiance  # type: ignore # noqa: PGH003

            forecasts.append(forecast)

        return forecasts

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        raise NotImplementedError
