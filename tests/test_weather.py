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
from homeassistant.const import CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.knmi import (
    KnmiDataUpdateCoordinator,
    async_setup_entry,
)
from custom_components.knmi.const import DOMAIN
from custom_components.knmi.weather import KnmiWeather
from .const import MOCK_CONFIG, MOCK_JSON


async def setup_weather(hass) -> KnmiWeather:
    """Setup weather entity."""

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    await async_setup_entry(hass, config_entry)

    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    return KnmiWeather(
        MOCK_CONFIG[CONF_NAME],
        coordinator,
        config_entry.entry_id,
    )


async def test_get_wind_bearing(hass, bypass_get_data):
    """Test get wind bearing function."""
    weather = await setup_weather(hass)

    # Test the case that the wind direction is variable.
    weather.coordinator.data = MOCK_JSON["liveweer"][0]
    weather.coordinator.data["windr"] = "VAR"
    weather.coordinator.data["windrgr"] = ""
    assert weather.get_wind_bearing("windr", "windrgr") == None

    # Test the case that the wind direction is not variable.
    weather.coordinator.data = MOCK_JSON["liveweer"][0]
    weather.coordinator.data["windr"] = "Zuid"
    weather.coordinator.data["windrgr"] = "180"
    assert weather.get_wind_bearing("windr", "windrgr") == 180


def map_condition(
    weather: KnmiWeather, api_condition: str | None, hass_condition: str | None
) -> None:
    """Helper method for testing wether condition"""
    weather.coordinator.data["image"] = api_condition
    assert weather.map_condition("image") == hass_condition


async def test_map_conditions(hass, bypass_get_data):
    """Test map condition function."""
    weather = await setup_weather(hass)
    weather.coordinator.data = MOCK_JSON["liveweer"][0]

    # Documented conditions.
    map_condition(weather, "zonnig", ATTR_CONDITION_SUNNY)
    map_condition(weather, "bliksem", ATTR_CONDITION_LIGHTNING)
    map_condition(weather, "regen", ATTR_CONDITION_RAINY)
    map_condition(weather, "buien", ATTR_CONDITION_POURING)
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
    map_condition(weather, "", None)
    map_condition(weather, "hondenweer", None)