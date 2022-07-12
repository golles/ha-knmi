"""Weather platform for knmi."""

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_NAME,
    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
)
from homeassistant.components.weather import (
    DOMAIN as SENSOR_DOMAIN,
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
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    Forecast,
    WeatherEntity,
)

from . import KnmiDataUpdateCoordinator
from .const import DEFAULT_NAME, DOMAIN

# Map weather conditions from KNMI to HA.
CONDITIONS_MAP = {
    "zonnig": ATTR_CONDITION_SUNNY,
    "bliksem": ATTR_CONDITION_LIGHTNING,
    "regen": ATTR_CONDITION_RAINY,
    "buien": ATTR_CONDITION_POURING,
    "hagel": ATTR_CONDITION_HAIL,
    "mist": ATTR_CONDITION_FOG,
    "sneeuw": ATTR_CONDITION_SNOWY,
    "bewolkt": ATTR_CONDITION_CLOUDY,
    "halfbewolkt": ATTR_CONDITION_PARTLYCLOUDY,
    "halfbewolkt_regen": ATTR_CONDITION_PARTLYCLOUDY,
    "zwaarbewolkt": ATTR_CONDITION_CLOUDY,
    "nachtmist": ATTR_CONDITION_FOG,
    "helderenacht": ATTR_CONDITION_CLEAR_NIGHT,
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
    """KNMI Weather class."""

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

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if self.coordinator.data.get("d0weer") is not None:
            return CONDITIONS_MAP[self.coordinator.data.get("d0weer")]
        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature in native units."""
        if self.coordinator.data.get("temp") is not None:
            return float(self.coordinator.data.get("temp"))
        return None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure in native units."""
        if self.coordinator.data.get("luchtd") is not None:
            return float(self.coordinator.data.get("luchtd"))
        return None

    @property
    def humidity(self) -> float | None:
        """Return the humidity in native units."""
        if self.coordinator.data.get("lv") is not None:
            return int(self.coordinator.data.get("lv"))
        return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed in native units."""
        if self.coordinator.data.get("windkmh") is not None:
            return float(self.coordinator.data.get("windkmh"))
        return None

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        if self.coordinator.data.get("windrgr") is not None:
            return int(self.coordinator.data.get("windrgr"))
        return None

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility in native units."""
        if self.coordinator.data.get("zicht") is not None:
            return int(self.coordinator.data.get("zicht"))
        return None

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast in native units."""
        forecast = []
        today = datetime.now()

        for i in range(0, 3):
            date = today + timedelta(days=i)
            condition = CONDITIONS_MAP[self.coordinator.data.get(f"d{i}weer", None)]
            wind_bearing = int(self.coordinator.data.get(f"d{i}windrgr", None))
            temp_low = float(self.coordinator.data.get(f"d{i}tmin", None))
            temp = float(self.coordinator.data.get(f"d{i}tmax", None))
            precipitation_probability = int(
                self.coordinator.data.get(f"d{i}neerslag", None)
            )
            wind_speed = float(self.coordinator.data.get(f"d{i}windkmh", None))
            sun_chance = int(self.coordinator.data.get(f"d{i}zon", None))
            next_day = {
                ATTR_FORECAST_TIME: date.isoformat(),
                ATTR_FORECAST_CONDITION: condition,
                ATTR_FORECAST_TEMP_LOW: temp_low,
                ATTR_FORECAST_TEMP: temp,
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: precipitation_probability,
                ATTR_FORECAST_WIND_BEARING: wind_bearing,
                ATTR_FORECAST_WIND_SPEED: wind_speed,
                "sun_chance": sun_chance,  # Not officially supported, but nice addition.
            }
            forecast.append(next_day)

        return forecast
