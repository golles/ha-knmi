"""Tests for knmi weather."""
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
