"""Tests for knmi sensor."""

from decimal import Decimal

from homeassistant.core import HomeAssistant

from . import setup_component


async def test_wind_sensor(hass: HomeAssistant, mocked_data):
    """Test wind sensor and attributes."""
    config_entry = await setup_component(hass)

    state = hass.states.get("sensor.knmi_home_wind")
    assert state.state == "10.8"
    assert state.attributes.get("richting") == "NO"
    assert state.attributes.get("graden") == 44
    assert state.attributes.get("beaufort") == 2
    assert Decimal(state.attributes.get("knopen")) == Decimal(5.8)

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()
