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

    @property
    def name(self):
        """Return the name of the sensor."""
        location = self.coordinator.data["plaats"]
        return f"{DEFAULT_NAME} {location}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.condition

    @property
    def condition(self):
        """Return the current condition."""
        return CONDITIONS_MAP[self.coordinator.data["d0weer"]]

    @property
    def temperature(self):
        """Return the temperature."""
        return float(self.coordinator.data["temp"])

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the pressure."""
        return float(self.coordinator.data["luchtd"])

    @property
    def humidity(self):
        """Return the humidity."""
        return float(self.coordinator.data["lv"])

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return float(self.coordinator.data["windkmh"])

    @property
    def wind_bearing(self):
        """Return the wind direction."""
        return WIND_DIRECTION_MAP[self.coordinator.data["windr"]]

    @property
    def visibility(self):
        """Return the wind direction."""
        return float(self.coordinator.data["zicht"]) / 10

    @property
    def forecast(self):
        """Return the forecast array."""
        forecast = []
        today = datetime.now()

        for i in range(0, 3):
            date = today + timedelta(days=i)
            nextDay = {
                ATTR_FORECAST_TIME: date.isoformat(),
                ATTR_FORECAST_CONDITION: CONDITIONS_MAP[
                    self.coordinator.data[f"d{i}weer"]
                ],
                ATTR_FORECAST_TEMP_LOW: float(self.coordinator.data[f"d{i}tmin"]),
                ATTR_FORECAST_TEMP: float(self.coordinator.data[f"d{i}tmax"]),
                ATTR_FORECAST_PRECIPITATION: float(
                    self.coordinator.data[f"d{i}neerslag"]
                ),
                ATTR_FORECAST_WIND_BEARING: WIND_DIRECTION_MAP[
                    self.coordinator.data[f"d{i}windr"]
                ],
                ATTR_FORECAST_WIND_SPEED: float(self.coordinator.data[f"d{i}windkmh"]),
            }
            forecast.append(nextDay)

        return forecast
