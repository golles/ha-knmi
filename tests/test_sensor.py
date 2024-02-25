"""Tests for knmi sensor."""

from decimal import Decimal

from homeassistant.core import HomeAssistant

from . import setup_component


async def test_states(hass: HomeAssistant, mocked_data):
    """Test all sensor states and attributes."""
    config_entry = await setup_component(hass)

    state = hass.states.get("sensor.knmi_dew_point")
    assert state.state == "10.1"

    state = hass.states.get("sensor.knmi_solar_irradiance")
    assert state.state == "0"

    state = hass.states.get("sensor.knmi_wind_chill")
    assert state.state == "6.8"

    state = hass.states.get("sensor.knmi_air_pressure")
    assert state.state == "1015.03"

    state = hass.states.get("sensor.knmi_humidity")
    assert state.state == "97"

    state = hass.states.get("sensor.knmi_max_temperature_today")
    assert state.state == "10"

    state = hass.states.get("sensor.knmi_max_temperature_tomorrow")
    assert state.state == "12"

    state = hass.states.get("sensor.knmi_min_temperature_today")
    assert state.state == "10"

    state = hass.states.get("sensor.knmi_min_temperature_tomorrow")
    assert state.state == "10"

    state = hass.states.get("sensor.knmi_precipitation_today")
    assert state.state == "0"

    state = hass.states.get("sensor.knmi_precipitation_tomorrow")
    assert state.state == "10"

    state = hass.states.get("sensor.knmi_location")
    assert state.state == "Purmerend"

    state = hass.states.get("sensor.knmi_remaining_api_requests")
    assert state.state == "132"

    state = hass.states.get("sensor.knmi_description")
    assert state.state == "Licht bewolkt"

    state = hass.states.get("sensor.knmi_temperature")
    assert state.state == "10.5"

    state = hass.states.get("sensor.knmi_latest_update")
    assert state.state == "2024-02-14T21:08:03+00:00"

    state = hass.states.get("sensor.knmi_weather_forecast")
    assert (
        state.state
        == "Bewolkt en perioden met regen. Morgen in de middag droog en zeer zacht"
    )

    state = hass.states.get("sensor.knmi_wind_speed")
    assert state.state == "29.1"
    assert state.attributes.get("bearing") == "WZW"
    assert state.attributes.get("degree") == 226
    assert state.attributes.get("beaufort") == 5
    assert Decimal(state.attributes.get("knots")) == Decimal(15.7)

    state = hass.states.get("sensor.knmi_weather_code")
    assert state.state == "groen"

    state = hass.states.get("sensor.knmi_visibility")
    assert state.state == "6990"

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()
