"""Weather platform for knmi."""
from datetime import timedelta
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
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    DOMAIN as SENSOR_DOMAIN,
    Forecast,
    WeatherEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt
import pytz

from . import KnmiDataUpdateCoordinator
from .const import API_TIMEZONE, DEFAULT_NAME, DOMAIN

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
                entry_id=entry.entry_id,
            )
        ]
    )


class KnmiWeather(WeatherEntity):
    """Defines a KNMI weather entity."""

    _attr_attribution = "KNMI Weergegevens via https://weerlive.nl"
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_visibility_unit = LENGTH_KILOMETERS
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR

    def __init__(
        self,
        conf_name: str,
        coordinator: KnmiDataUpdateCoordinator,
        entry_id: str,
    ):
        self.coordinator = coordinator

        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{conf_name}".lower()
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {conf_name}"
        self._attr_device_info = coordinator.device_info

    def map_condition(self, key: str | None) -> str | None:
        """Map weather conditions from KNMI to HA."""
        value = self.coordinator.get_value(key)
        if "".__eq__(value):
            return None

        try:
            return CONDITIONS_MAP[value]
        except KeyError:
            _LOGGER.error(
                "Weather condition %s (for %s) is unknown, please raise a bug",
                value,
                key,
            )
        return None

    def get_wind_bearing(
        self, wind_dir_key: str, wind_dir_degree_key: str
    ) -> float | None:
        """Get the wind bearing, handle variable (VAR) direction as None."""
        wind_dir = self.coordinator.get_value(wind_dir_key)
        if wind_dir == "VAR":
            _LOGGER.debug(
                "There is light wind from variable wind directions for %s, so no value",
                wind_dir_key,
            )
            return None

        return self.coordinator.get_value(wind_dir_degree_key, float)

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        return self.map_condition("image")

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature in native units."""
        return self.coordinator.get_value("temp", float)

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure in native units."""
        return self.coordinator.get_value("luchtd", float)

    @property
    def humidity(self) -> float | None:
        """Return the humidity in native units."""
        return self.coordinator.get_value("lv", float)

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed in native units."""
        return self.coordinator.get_value("windkmh", float)

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        return self.get_wind_bearing("windr", "windrgr")

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility in native units."""
        return self.coordinator.get_value("zicht", float)

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast in native units."""
        forecast = []
        timezone = pytz.timezone(API_TIMEZONE)
        today = dt.as_utc(
            dt.now(timezone).replace(hour=0, minute=0, second=0, microsecond=0)
        )

        for i in range(0, 3):
            date = today + timedelta(days=i)
            condition = self.map_condition(f"d{i}weer")
            wind_bearing = self.get_wind_bearing(f"d{i}windr", f"d{i}windrgr")
            temp_low = self.coordinator.get_value(f"d{i}tmin", float)
            temp = self.coordinator.get_value(f"d{i}tmax", float)
            precipitation_probability = self.coordinator.get_value(
                f"d{i}neerslag", float
            )
            wind_speed = self.coordinator.get_value(f"d{i}windkmh", float)
            sun_chance = self.coordinator.get_value(f"d{i}zon", float)
            wind_speed_bft = self.coordinator.get_value(f"d{i}windk", float)
            next_day = {
                ATTR_FORECAST_TIME: date.isoformat(),
                ATTR_FORECAST_CONDITION: condition,
                ATTR_FORECAST_TEMP_LOW: temp_low,
                ATTR_FORECAST_TEMP: temp,
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: precipitation_probability,
                ATTR_FORECAST_WIND_BEARING: wind_bearing,
                ATTR_FORECAST_WIND_SPEED: wind_speed,
                # Not officially supported, but nice additions.
                "wind_speed_bft": wind_speed_bft,
                "sun_chance": sun_chance,
            }
            forecast.append(next_day)

        return forecast
