"""Tests for knmi sensor."""
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi import async_setup_entry
from custom_components.knmi.const import DOMAIN

from .const import MOCK_CONFIG


async def test_wind_sensor(hass: HomeAssistant, mocked_data):
    """Test wind sensor and attributes."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.knmi_home_wind")
    assert state.state == "10.8"
    assert state.attributes.get("richting") == "NO"
    assert state.attributes.get("graden") == 44
    assert state.attributes.get("beaufort") == 2
    assert state.attributes.get("knopen") == 5.8
