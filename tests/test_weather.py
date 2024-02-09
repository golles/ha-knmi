"""Tests for knmi weather."""

from decimal import Decimal

from freezegun import freeze_time
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

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator
from custom_components.knmi.weather import KnmiWeather

from . import setup_component


async def test_get_wind_bearing(hass: HomeAssistant, mocked_data, caplog):
    """Test get wind bearing function."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator, config_entry.entry_id)

    # Test the case that the wind direction is variable.
    weather.coordinator.data["windr"] = "VAR"
    weather.coordinator.data["windrgr"] = ""
    assert weather.get_wind_bearing("windr", "windrgr") == None
    assert (
        "There is light wind from variable wind directions for windr, so no value"
        in caplog.text
    )

    # Test the case that the wind direction is not variable.
    weather.coordinator.data["windr"] = "Zuid"
    weather.coordinator.data["windrgr"] = "180"
    assert weather.get_wind_bearing("windr", "windrgr") == 180

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


def map_condition(
    weather: KnmiWeather, api_condition: str | None, hass_condition: str | None
) -> None:
    """Helper method for testing wether condition"""
    weather.coordinator.data["image"] = api_condition
    assert weather.map_condition("image") == hass_condition


async def test_map_conditions(hass: HomeAssistant, mocked_data, caplog):
    """Test map condition function."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator, config_entry.entry_id)

    # Documented conditions.
    map_condition(weather, "zonnig", ATTR_CONDITION_SUNNY)
    map_condition(weather, "bliksem", ATTR_CONDITION_LIGHTNING)
    map_condition(weather, "regen", ATTR_CONDITION_POURING)
    map_condition(weather, "buien", ATTR_CONDITION_RAINY)
    map_condition(weather, "hagel", ATTR_CONDITION_HAIL)
    map_condition(weather, "mist", ATTR_CONDITION_FOG)
    map_condition(weather, "sneeuw", ATTR_CONDITION_SNOWY)
    map_condition(weather, "bewolkt", ATTR_CONDITION_CLOUDY)
    map_condition(weather, "lichtbewolkt", ATTR_CONDITION_PARTLYCLOUDY)
    map_condition(weather, "halfbewolkt", ATTR_CONDITION_PARTLYCLOUDY)
    map_condition(weather, "halfbewolkt_regen", ATTR_CONDITION_RAINY)
    map_condition(weather, "zwaarbewolkt", ATTR_CONDITION_CLOUDY)
    map_condition(weather, "nachtmist", ATTR_CONDITION_FOG)
    map_condition(weather, "helderenacht", ATTR_CONDITION_CLEAR_NIGHT)
    map_condition(weather, "nachtbewolkt", ATTR_CONDITION_CLOUDY)

    # Undocumented conditions.
    map_condition(weather, "wolkennacht", ATTR_CONDITION_CLOUDY)

    # Error cases.
    map_condition(weather, None, None)
    assert (
        "Weather condition None (for image) is unknown, please raise a bug"
        in caplog.text
    )
    map_condition(weather, "", None)
    map_condition(weather, "hondenweer", None)
    assert (
        "Weather condition hondenweer (for image) is unknown, please raise a bug"
        in caplog.text
    )

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_state(hass: HomeAssistant, mocked_data):
    """Test state."""
    config_entry = await setup_component(hass)

    state = hass.states.get("weather.knmi_home")
    assert state

    assert state.state == "partlycloudy"

    assert state.attributes.get(ATTR_WEATHER_HUMIDITY) == 86
    assert Decimal(state.attributes.get(ATTR_WEATHER_PRESSURE)) == Decimal(1024.0)
    assert Decimal(state.attributes.get(ATTR_WEATHER_TEMPERATURE)) == Decimal(17.5)
    assert Decimal(state.attributes.get(ATTR_WEATHER_VISIBILITY)) == Decimal(45.0)
    assert Decimal(state.attributes.get(ATTR_WEATHER_WIND_BEARING)) == Decimal(44.0)
    assert Decimal(state.attributes.get(ATTR_WEATHER_WIND_SPEED)) == Decimal(10.8)
    assert state.attributes.get(ATTR_WEATHER_DEW_POINT) == 15

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


@freeze_time("2023-07-29T22:00:00+00:00")
async def test_async_forecast_daily(hass: HomeAssistant, mocked_data):
    """Test forecast."""
    config_entry = await setup_component(hass)
    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    weather = KnmiWeather(config_entry, coordinator, config_entry.entry_id)

    forecast = await weather.async_forecast_daily()
    assert forecast
    assert len(forecast) == 3

    assert forecast[0][ATTR_FORECAST_TIME] == "2023-07-29T22:00:00+00:00"
    assert forecast[0][ATTR_FORECAST_CONDITION] == "cloudy"
    assert Decimal(forecast[0][ATTR_FORECAST_TEMP_LOW]) == Decimal(14.0)
    assert Decimal(forecast[0][ATTR_FORECAST_TEMP]) == Decimal(21.0)
    assert Decimal(forecast[0][ATTR_FORECAST_PRECIPITATION_PROBABILITY]) == Decimal(0.0)
    assert Decimal(forecast[0][ATTR_FORECAST_WIND_BEARING]) == Decimal(135.0)
    assert Decimal(forecast[0][ATTR_FORECAST_WIND_SPEED]) == Decimal(11.0)
    assert Decimal(forecast[0]["wind_speed_bft"]) == Decimal(2.0)
    assert Decimal(forecast[0]["sun_chance"]) == Decimal(14.0)

    assert forecast[1][ATTR_FORECAST_TIME] == "2023-07-30T22:00:00+00:00"
    assert forecast[1][ATTR_FORECAST_CONDITION] == "partlycloudy"
    assert Decimal(forecast[1][ATTR_FORECAST_TEMP_LOW]) == Decimal(13.0)
    assert Decimal(forecast[1][ATTR_FORECAST_TEMP]) == Decimal(28.0)
    assert Decimal(forecast[1][ATTR_FORECAST_PRECIPITATION_PROBABILITY]) == Decimal(
        10.0
    )
    assert Decimal(forecast[1][ATTR_FORECAST_WIND_BEARING]) == Decimal(225.0)
    assert Decimal(forecast[1][ATTR_FORECAST_WIND_SPEED]) == Decimal(7.0)
    assert Decimal(forecast[1]["wind_speed_bft"]) == Decimal(2.0)
    assert Decimal(forecast[1]["sun_chance"]) == Decimal(60.0)

    assert forecast[2][ATTR_FORECAST_TIME] == "2023-07-31T22:00:00+00:00"
    assert forecast[2][ATTR_FORECAST_CONDITION] == "cloudy"
    assert Decimal(forecast[2][ATTR_FORECAST_TEMP_LOW]) == Decimal(18.0)
    assert Decimal(forecast[2][ATTR_FORECAST_TEMP]) == Decimal(24.0)
    assert Decimal(forecast[2][ATTR_FORECAST_PRECIPITATION_PROBABILITY]) == Decimal(
        20.0
    )
    assert Decimal(forecast[2][ATTR_FORECAST_WIND_BEARING]) == Decimal(315.0)
    assert Decimal(forecast[2][ATTR_FORECAST_WIND_SPEED]) == Decimal(11.0)
    assert Decimal(forecast[2]["wind_speed_bft"]) == Decimal(2.0)
    assert Decimal(forecast[2]["sun_chance"]) == Decimal(30.0)
