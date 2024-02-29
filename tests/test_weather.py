"""Tests for knmi weather."""

from decimal import Decimal

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
    ATTR_WEATHER_DEW_POINT,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_VISIBILITY,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
)
from homeassistant.core import HomeAssistant
import pytest

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator
from custom_components.knmi.weather import KnmiWeather

from . import setup_component


async def test_map_conditions(hass: HomeAssistant, mocked_data, caplog):
    """Test map condition function."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator)

    # Documented conditions.
    assert weather.map_condition("zonnig") == ATTR_CONDITION_SUNNY
    assert weather.map_condition("bliksem") == ATTR_CONDITION_LIGHTNING
    assert weather.map_condition("regen") == ATTR_CONDITION_POURING
    assert weather.map_condition("buien") == ATTR_CONDITION_RAINY
    assert weather.map_condition("hagel") == ATTR_CONDITION_HAIL
    assert weather.map_condition("mist") == ATTR_CONDITION_FOG
    assert weather.map_condition("sneeuw") == ATTR_CONDITION_SNOWY
    assert weather.map_condition("bewolkt") == ATTR_CONDITION_CLOUDY
    assert weather.map_condition("lichtbewolkt") == ATTR_CONDITION_PARTLYCLOUDY
    assert weather.map_condition("halfbewolkt") == ATTR_CONDITION_PARTLYCLOUDY
    assert weather.map_condition("halfbewolkt_regen") == ATTR_CONDITION_RAINY
    assert weather.map_condition("zwaarbewolkt") == ATTR_CONDITION_CLOUDY
    assert weather.map_condition("nachtmist") == ATTR_CONDITION_FOG
    assert weather.map_condition("helderenacht") == ATTR_CONDITION_CLEAR_NIGHT
    assert weather.map_condition("nachtbewolkt") == ATTR_CONDITION_CLOUDY

    # # Undocumented conditions.
    assert weather.map_condition("wolkennacht") == ATTR_CONDITION_CLOUDY

    # Error cases.
    assert weather.map_condition(None) is None
    assert (
        'Weather condition "None" can\'t be mapped, please raise a bug' in caplog.text
    )
    assert weather.map_condition("") is None
    assert 'Weather condition "" can\'t be mapped, please raise a bug' in caplog.text
    assert weather.map_condition("hondenweer") is None
    assert (
        'Weather condition "hondenweer" can\'t be mapped, please raise a bug'
        in caplog.text
    )

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_state(hass: HomeAssistant, mocked_data):
    """Test state."""
    config_entry = await setup_component(hass)

    state = hass.states.get("weather.knmi_home")
    assert state

    assert state.state == "cloudy"

    assert state.attributes.get(ATTR_WEATHER_HUMIDITY) == 97
    assert Decimal(state.attributes.get(ATTR_WEATHER_PRESSURE)) == Decimal(1015.03)
    assert Decimal(state.attributes.get(ATTR_WEATHER_TEMPERATURE)) == Decimal(10.5)
    assert Decimal(state.attributes.get(ATTR_WEATHER_VISIBILITY)) == Decimal(6.99)
    assert Decimal(state.attributes.get(ATTR_WEATHER_WIND_BEARING)) == 226
    assert Decimal(state.attributes.get(ATTR_WEATHER_WIND_SPEED)) == Decimal(29.1)
    assert Decimal(state.attributes.get(ATTR_WEATHER_DEW_POINT)) == Decimal(10.1)

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_async_forecast_daily(hass: HomeAssistant, mocked_data):
    """Test daily forecast."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator)

    forecast = await weather.async_forecast_daily()
    assert forecast
    assert len(forecast) == 5

    assert forecast[0][ATTR_FORECAST_TIME] == "2024-02-14T00:00:00+01:00"
    assert forecast[0][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[0][ATTR_FORECAST_TEMP_LOW] == 10
    assert forecast[0][ATTR_FORECAST_TEMP] == 10
    assert forecast[0][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[0][ATTR_FORECAST_WIND_BEARING] == 221
    assert forecast[0][ATTR_FORECAST_WIND_SPEED] == 25
    assert forecast[0]["wind_speed_bft"] == 4
    assert forecast[0]["sun_chance"] == 0

    assert forecast[1][ATTR_FORECAST_TIME] == "2024-02-15T00:00:00+01:00"
    assert forecast[1][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[1][ATTR_FORECAST_TEMP_LOW] == 10
    assert forecast[1][ATTR_FORECAST_TEMP] == 12
    assert forecast[1][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 10
    assert forecast[1][ATTR_FORECAST_WIND_BEARING] == 184
    assert forecast[1][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[1]["wind_speed_bft"] == 3
    assert forecast[1]["sun_chance"] == 8

    assert forecast[2][ATTR_FORECAST_TIME] == "2024-02-16T00:00:00+01:00"
    assert forecast[2][ATTR_FORECAST_CONDITION] == "rainy"
    assert forecast[2][ATTR_FORECAST_TEMP_LOW] == 9
    assert forecast[2][ATTR_FORECAST_TEMP] == 10
    assert forecast[2][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 40
    assert forecast[2][ATTR_FORECAST_WIND_BEARING] == 199
    assert forecast[2][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[2]["wind_speed_bft"] == 3
    assert forecast[2]["sun_chance"] == 14

    assert forecast[3][ATTR_FORECAST_TIME] == "2024-02-17T00:00:00+01:00"
    assert forecast[3][ATTR_FORECAST_CONDITION] == "partlycloudy"
    assert forecast[3][ATTR_FORECAST_TEMP_LOW] == 6
    assert forecast[3][ATTR_FORECAST_TEMP] == 8
    assert forecast[3][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 20
    assert forecast[3][ATTR_FORECAST_WIND_BEARING] == 228
    assert forecast[3][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[3]["wind_speed_bft"] == 3
    assert forecast[3]["sun_chance"] == 46

    assert forecast[4][ATTR_FORECAST_TIME] == "2024-02-18T00:00:00+01:00"
    assert forecast[4][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[4][ATTR_FORECAST_TEMP_LOW] == 7
    assert forecast[4][ATTR_FORECAST_TEMP] == 8
    assert forecast[4][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 10
    assert forecast[4][ATTR_FORECAST_WIND_BEARING] == 210
    assert forecast[4][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[4]["wind_speed_bft"] == 3
    assert forecast[4]["sun_chance"] == 0

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_async_forecast_hourly(hass: HomeAssistant, mocked_data):
    """Test hourly forecast."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator)

    forecast = await weather.async_forecast_hourly()
    assert forecast
    assert len(forecast) == 24

    assert forecast[0][ATTR_FORECAST_TIME] == "2024-02-14T23:00:00+01:00"
    assert forecast[0][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[0][ATTR_FORECAST_TEMP] == 10
    assert forecast[0][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[0][ATTR_FORECAST_WIND_BEARING] == 231
    assert forecast[0][ATTR_FORECAST_WIND_SPEED] == 21
    assert forecast[0]["wind_speed_bft"] == 4
    assert forecast[0]["solar_irradiance"] == 0

    assert forecast[3][ATTR_FORECAST_TIME] == "2024-02-15T02:00:00+01:00"
    assert forecast[3][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[3][ATTR_FORECAST_TEMP] == 10
    assert forecast[3][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[3][ATTR_FORECAST_WIND_BEARING] == 226
    assert forecast[3][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[3]["wind_speed_bft"] == 3
    assert forecast[3]["solar_irradiance"] == 0

    assert forecast[5][ATTR_FORECAST_TIME] == "2024-02-15T04:00:00+01:00"
    assert forecast[5][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[5][ATTR_FORECAST_TEMP] == 10
    assert forecast[5][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[5][ATTR_FORECAST_WIND_BEARING] == 219
    assert forecast[5][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[5]["wind_speed_bft"] == 3
    assert forecast[5]["solar_irradiance"] == 0

    assert forecast[8][ATTR_FORECAST_TIME] == "2024-02-15T07:00:00+01:00"
    assert forecast[8][ATTR_FORECAST_CONDITION] == "pouring"
    assert forecast[8][ATTR_FORECAST_TEMP] == 10
    assert Decimal(forecast[8][ATTR_FORECAST_PRECIPITATION_PROBABILITY]) == Decimal(0.9)
    assert forecast[8][ATTR_FORECAST_WIND_BEARING] == 196
    assert forecast[8][ATTR_FORECAST_WIND_SPEED] == 14
    assert forecast[8]["wind_speed_bft"] == 3
    assert forecast[8]["solar_irradiance"] == 0

    assert forecast[13][ATTR_FORECAST_TIME] == "2024-02-15T12:00:00+01:00"
    assert forecast[13][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[13][ATTR_FORECAST_TEMP] == 12
    assert forecast[13][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[13][ATTR_FORECAST_WIND_BEARING] == 206
    assert forecast[13][ATTR_FORECAST_WIND_SPEED] == 14
    assert forecast[13]["wind_speed_bft"] == 3
    assert forecast[13]["solar_irradiance"] == 30

    assert forecast[18][ATTR_FORECAST_TIME] == "2024-02-15T17:00:00+01:00"
    assert forecast[18][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[18][ATTR_FORECAST_TEMP] == 14
    assert forecast[18][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[18][ATTR_FORECAST_WIND_BEARING] == 168
    assert forecast[18][ATTR_FORECAST_WIND_SPEED] == 14
    assert forecast[18]["wind_speed_bft"] == 3
    assert forecast[18]["solar_irradiance"] == 72

    assert forecast[23][ATTR_FORECAST_TIME] == "2024-02-15T22:00:00+01:00"
    assert forecast[23][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[23][ATTR_FORECAST_TEMP] == 12
    assert forecast[23][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[23][ATTR_FORECAST_WIND_BEARING] == 162
    assert forecast[23][ATTR_FORECAST_WIND_SPEED] == 18
    assert forecast[23]["wind_speed_bft"] == 3
    assert forecast[23]["solar_irradiance"] == 0

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_async_forecast_twice_daily(hass: HomeAssistant, mocked_data):
    """Test twice daily forecast."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator)

    with pytest.raises(NotImplementedError):
        await weather.async_forecast_twice_daily()

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()
