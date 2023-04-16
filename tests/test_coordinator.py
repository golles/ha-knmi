"""Tests for knmi coordinator."""
from homeassistant.core import HomeAssistant

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator

from . import setup_component


async def test_get_value(hass: HomeAssistant, mocked_data, caplog):
    """Test get_value return types."""
    config_entry = await setup_component(hass)

    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    assert coordinator.get_value("temp", float) == 17.5
    assert coordinator.get_value("temp", str) == "17.5"
    coordinator.get_value("temp", int)
    assert "Value temp can't be converted to <class 'int'>" in caplog.text

    assert coordinator.get_value("lv", int) == 86
    assert coordinator.get_value("lv", float) == 86.0
    assert coordinator.get_value("lv", str) == "86"

    assert coordinator.get_value("plaats", str) == "Purmerend"
    coordinator.get_value("plaats", int)
    assert "Value plaats can't be converted to <class 'int'>" in caplog.text
    coordinator.get_value("plaats", float)
    assert "Value plaats can't be converted to <class 'float'>" in caplog.text

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()


async def test_get_value_empty(hass: HomeAssistant, mocked_data_empty_values, caplog):
    """Test get_value function with empty values."""
    config_entry = await setup_component(hass)

    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    coordinator.get_value("plaats")
    assert "Value plaats is missing in API response" in caplog.text

    coordinator.get_value("temp", int)
    assert "Value temp can't be converted to <class 'int'>" in caplog.text

    assert await config_entry.async_unload(hass)
    await hass.async_block_till_done()
