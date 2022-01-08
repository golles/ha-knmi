"""Weather platform for knmi."""

from datetime import datetime, timedelta

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    WeatherEntity,
)
from homeassistant.const import (
    CONF_NAME,
    TEMP_CELSIUS,
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
    def state(self):
        """Return the state of the sensor."""
        return self.condition

    @property
    def condition(self):
        """Return the current condition."""
        if super().getData("d0weer") is not None:
            return CONDITIONS_MAP[super().getData("d0weer")]

    @property
    def temperature(self):
        """Return the temperature."""
        if super().getData("temp") is not None:
            return float(super().getData("temp"))

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the pressure."""
        if super().getData("luchtd") is not None:
            return float(super().getData("luchtd"))

    @property
    def humidity(self):
        """Return the humidity."""
        if super().getData("lv") is not None:
            return float(super().getData("lv"))

    @property
    def wind_speed(self):
        """Return the wind speed."""
        if super().getData("windkmh") is not None:
            return float(super().getData("windkmh"))

    @property
    def wind_bearing(self):
        """Return the wind direction."""
        if super().getData("windr") is not None:
            return WIND_DIRECTION_MAP[super().getData("windr")]

    @property
    def visibility(self):
        """Return the wind direction."""
        if super().getData("zicht") is not None:
            return float(super().getData("zicht")) / 10

    @property
    def forecast(self):
        """Return the forecast array."""
        forecast = []
        today = datetime.now()

        for i in range(0, 3):
            date = today + timedelta(days=i)
            condition = (
                CONDITIONS_MAP[super().getData(f"d{i}weer")]
                if super().getData(f"d{i}weer") is not None
                else None
            )
            wind_bearing = (
                WIND_DIRECTION_MAP[super().getData(f"d{i}windr")]
                if super().getData(f"d{i}windr") is not None
                else None
            )
            temp_low = (
                float(super().getData(f"d{i}tmin"))
                if super().getData(f"d{i}tmin") is not None
                else None
            )
            temp = (
                float(super().getData(f"d{i}tmax"))
                if super().getData(f"d{i}tmax") is not None
                else None
            )
            precipitation = (
                float(super().getData(f"d{i}neerslag"))
                if super().getData(f"d{i}neerslag") is not None
                else None
            )
            wind_speed = (
                float(super().getData(f"d{i}windkmh"))
                if super().getData(f"d{i}windkmh") is not None
                else None
            )
            next_day = {
                ATTR_FORECAST_TIME: date.isoformat(),
                ATTR_FORECAST_CONDITION: condition,
                ATTR_FORECAST_TEMP_LOW: temp_low,
                ATTR_FORECAST_TEMP: temp,
                ATTR_FORECAST_PRECIPITATION: precipitation,
                ATTR_FORECAST_WIND_BEARING: wind_bearing,
                ATTR_FORECAST_WIND_SPEED: wind_speed,
            }
            forecast.append(next_day)

        return forecast
