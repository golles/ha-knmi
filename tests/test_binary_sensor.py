"""Tests for knmi binary_sensor."""

from freezegun import freeze_time
from homeassistant.core import HomeAssistant

from . import setup_component


async def test_knmi_binary_alarm_sensor_is_off(hass: HomeAssistant, mocked_data):
    """Test is_on function on alarm sensor."""
    config_entry = await setup_component(hass)

    state = hass.states.get("binary_sensor.knmi_warning")
    assert state.state == "off"
    assert state.attributes.get("title") == "Er zijn geen waarschuwingen"
    assert (
        state.attributes.get("description")
        == "Er zijn momenteel geen waarschuwingen van kracht."
    )
    assert state.attributes.get("code") == "groen"

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_knmi_binary_alarm_sensor_is_on(hass: HomeAssistant, mocked_data_alarm):
    """Test is_on function on alarm sensor."""
    config_entry = await setup_component(hass)

    state = hass.states.get("binary_sensor.knmi_warning")
    assert state.state == "on"
    assert state.attributes.get("title") == "Gladheid"
    assert (
        state.attributes.get("description")
        == "Code geel in bijna hele land vanwege gladheid"
    )
    assert state.attributes.get("code") == "geel"

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


@freeze_time("2023-02-05T03:30:00+01:00")
async def test_knmi_binary_sun_sensor_is_off(hass: HomeAssistant, mocked_data):
    """Test is_on function on sun sensor."""
    config_entry = await setup_component(hass)

    state = hass.states.get("binary_sensor.knmi_sun")
    assert state.state == "off"
    assert str(state.attributes.get("sunrise")) == "2023-02-05 07:57:00+01:00"
    assert str(state.attributes.get("sunset")) == "2023-02-05 17:51:00+01:00"
    assert state.attributes.get("sun_chance0") == 0
    assert state.attributes.get("sun_chance1") == 8
    assert state.attributes.get("sun_chance2") == 14

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


@freeze_time("2023-02-05T15:30:00+00:00")
async def test_knmi_binary_sun_sensor_is_on(hass: HomeAssistant, mocked_data):
    """Test is_on function on sun sensor."""
    config_entry = await setup_component(hass)

    state = hass.states.get("binary_sensor.knmi_sun")
    assert state.state == "on"

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()
