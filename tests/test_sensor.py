"""Tests for sensor."""

import pytest
from homeassistant.core import HomeAssistant

from . import setup_integration, unload_integration


@pytest.mark.parametrize(
    ("entity", "value"),
    [
        ("sensor.home_dew_point", "10.1"),
        ("sensor.home_solar_irradiance", "0"),
        ("sensor.home_wind_chill", "6.8"),
        ("sensor.home_air_pressure", "1015.03"),
        ("sensor.home_humidity", "97"),
        ("sensor.home_max_temperature_today", "10.0"),
        ("sensor.home_max_temperature_tomorrow", "12.0"),
        ("sensor.home_min_temperature_today", "10.0"),
        ("sensor.home_min_temperature_tomorrow", "10.0"),
        ("sensor.home_precipitation_today", "0"),
        ("sensor.home_precipitation_tomorrow", "10"),
        ("sensor.home_location", "Purmerend"),
        ("sensor.home_remaining_api_requests", "132"),
        ("sensor.home_description", "Licht bewolkt"),
        ("sensor.home_temperature", "10.5"),
        ("sensor.home_latest_update", "2024-02-14T21:08:03+00:00"),
        ("sensor.home_weather_forecast", "Bewolkt en perioden met regen. Morgen in de middag droog en zeer zacht"),
        ("sensor.home_wind_speed", "29.1"),
        ("sensor.home_weather_code", "groen"),
        ("sensor.home_visibility", "6990"),
    ],
)
@pytest.mark.usefixtures("mocked_data")
async def test_state(hass: HomeAssistant, entity: str, value: str) -> None:
    """Test sensor state."""
    config_entry = await setup_integration(hass)

    state = hass.states.get(entity)
    assert state
    assert state.state == value

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mocked_data")
async def test_state_with_attributes(hass: HomeAssistant) -> None:
    """Test sensor state."""
    config_entry = await setup_integration(hass)

    state = hass.states.get("sensor.home_wind_speed")
    assert state
    assert state.state == "29.1"
    assert state.attributes.get("bearing") == "WZW"
    assert state.attributes.get("degree") == 226
    assert state.attributes.get("beaufort") == 5
    assert (str(state.attributes.get("knots"))) == "15.7"

    await unload_integration(hass, config_entry)
