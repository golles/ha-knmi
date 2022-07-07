"""Weather platform for knmi."""

from datetime import datetime, timedelta

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    WeatherEntity,
)
from homeassistant.const import (
    CONF_NAME,
)

from .const import CONDITIONS_MAP, DEFAULT_NAME, DOMAIN, WIND_DIRECTION_MAP
from .entity import KnmiEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([KnmiWeather(coordinator, entry)])


class KnmiWeather(KnmiEntity, WeatherEntity):
    """knmi Weather class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self.entry_name = config_entry.data.get(CONF_NAME)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME} {self.entry_name}"

    @property
    def condition(self):
        """Return the current condition."""
        if super().get_data("d0weer") is not None:
            return CONDITIONS_MAP[super().get_data("d0weer")]
        return None

    @property
    def native_temperature(self):
        """Return the temperature."""
        if super().get_data("temp") is not None:
            return float(super().get_data("temp"))
        return None

    @property
    def native_pressure(self):
        """Return the pressure."""
        if super().get_data("luchtd") is not None:
            return float(super().get_data("luchtd"))
        return None

    @property
    def native_humidity(self):
        """Return the humidity."""
        if super().get_data("lv") is not None:
            return float(super().get_data("lv"))
        return None

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        if super().get_data("windkmh") is not None:
            return float(super().get_data("windkmh"))
        return None

    @property
    def wind_bearing(self):
        """Return the wind direction."""
        if super().get_data("windr") is not None:
            return WIND_DIRECTION_MAP[super().get_data("windr")]
        return None

    @property
    def native_visibility(self):
        """Return the wind direction."""
        if super().get_data("zicht") is not None:
            return float(super().get_data("zicht"))
        return None

    @property
    def forecast(self):
        """Return the forecast array."""
        forecast = []
        today = datetime.now()

        for i in range(0, 3):
            date = today + timedelta(days=i)
            condition = (
                CONDITIONS_MAP[super().get_data(f"d{i}weer")]
                if super().get_data(f"d{i}weer") is not None
                else None
            )
            wind_bearing = (
                WIND_DIRECTION_MAP[super().get_data(f"d{i}windr")]
                if super().get_data(f"d{i}windr") is not None
                else None
            )
            temp_low = (
                float(super().get_data(f"d{i}tmin"))
                if super().get_data(f"d{i}tmin") is not None
                else None
            )
            temp = (
                float(super().get_data(f"d{i}tmax"))
                if super().get_data(f"d{i}tmax") is not None
                else None
            )
            precipitation_probability = (
                float(super().get_data(f"d{i}neerslag"))
                if super().get_data(f"d{i}neerslag") is not None
                else None
            )
            wind_speed = (
                float(super().get_data(f"d{i}windkmh"))
                if super().get_data(f"d{i}windkmh") is not None
                else None
            )
            sun_chance = (
                float(super().get_data(f"d{i}zon"))
                if super().get_data(f"d{i}zon") is not None
                else None
            )
            next_day = {
                ATTR_FORECAST_TIME: date.isoformat(),
                ATTR_FORECAST_CONDITION: condition,
                ATTR_FORECAST_TEMP_LOW: temp_low,
                ATTR_FORECAST_TEMP: temp,
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: precipitation_probability,
                ATTR_FORECAST_WIND_BEARING: wind_bearing,
                ATTR_FORECAST_WIND_SPEED: wind_speed,
                "sun_chance": sun_chance,
            }
            forecast.append(next_day)

        return forecast
