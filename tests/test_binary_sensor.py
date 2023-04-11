"""Tests for knmi binary_sensor."""
from freezegun import freeze_time
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi import async_setup_entry
from custom_components.knmi.binary_sensor import KnmiBinarySensor
from custom_components.knmi.const import DOMAIN

from .const import MOCK_CONFIG


async def test_knmi_binary_sensor_is_on(hass: HomeAssistant, mocked_data):
    """Test is_on function on base class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    binary_sensor = KnmiBinarySensor(
        MOCK_CONFIG[CONF_NAME],
        hass.data[DOMAIN][config_entry.entry_id],
        config_entry.entry_id,
        SensorEntityDescription(
            key="key",
            name="name",
        ),
    )

    with pytest.raises(NotImplementedError):
        binary_sensor.is_on


async def test_knmi_binary_alarm_sensor_is_off(hass: HomeAssistant, mocked_data):
    """Test is_on function on alarm class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.knmi_home_waarschuwing")
    assert state.state == "off"
    assert state.attributes.get("Waarschuwing") == ""


async def test_knmi_binary_alarm_sensor_is_on(hass: HomeAssistant, mocked_data_alarm):
    """Test is_on function on alarm class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.knmi_home_waarschuwing")
    assert state.state == "on"
    assert (
        state.attributes.get("Waarschuwing")
        == "Code geel in bijna hele land vanwege gladheid"
    )


@freeze_time("2023-02-05T03:30:00+00:00")
async def test_knmi_binary_sun_sensor_is_off(hass: HomeAssistant, mocked_data):
    """Test is_on function on alarm class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.knmi_home_zon")
    assert state.state == "off"
    assert state.attributes.get("Zonsopkomst") == "2023-02-05T04:27:00+00:00"
    assert state.attributes.get("Zonondergang") == "2023-02-05T21:03:00+00:00"
    assert state.attributes.get("Zonkans vandaag") == 14
    assert state.attributes.get("Zonkans morgen") == 60
    assert state.attributes.get("Zonkans overmorgen") == 30


@freeze_time("2023-02-05T15:30:00+00:00")
async def test_knmi_binary_sun_sensor_is_on(hass: HomeAssistant, mocked_data):
    """Test is_on function on alarm class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.knmi_home_zon")
    assert state.state == "on"
