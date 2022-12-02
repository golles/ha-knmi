"""Tests for knmi binary_sensor."""

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import CONF_NAME
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi import async_setup_entry
from custom_components.knmi.binary_sensor import KnmiBinaryAlarmSensor, KnmiBinarySensor
from custom_components.knmi.const import DOMAIN

from .const import MOCK_CONFIG, MOCK_JSON


@pytest.mark.asyncio
async def test_knmi_binary_sensor_is_on(hass, bypass_get_data):
    """Test is_on function on base class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    await async_setup_entry(hass, config_entry)

    binary_sensor = KnmiBinarySensor(
        MOCK_CONFIG[CONF_NAME],
        hass.data[DOMAIN][config_entry.entry_id],
        config_entry.entry_id,
        SensorEntityDescription(
            key="key",
            name="name",
        ),
    )
    binary_sensor.coordinator.data = MOCK_JSON["liveweer"][0]

    with pytest.raises(NotImplementedError):
        binary_sensor.is_on


@pytest.mark.asyncio
async def test_knmi_binary_alarm_sensor_is_on(hass, bypass_get_data):
    """Test is_on function on alarm class."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    await async_setup_entry(hass, config_entry)

    alarm_sensor = KnmiBinaryAlarmSensor(
        MOCK_CONFIG[CONF_NAME],
        hass.data[DOMAIN][config_entry.entry_id],
        config_entry.entry_id,
        SensorEntityDescription(
            key="alarm",
            name="alarm",
        ),
    )
    alarm_sensor.coordinator.data = MOCK_JSON["liveweer"][0]

    alarm_sensor.coordinator.data["alarm"] = "1"
    assert alarm_sensor.is_on
    alarm_sensor.coordinator.data["alarm"] = "0"
    assert alarm_sensor.is_on is False
