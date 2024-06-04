"""Tests for knmi coordinator."""

from decimal import Decimal

from freezegun import freeze_time
from homeassistant.core import HomeAssistant

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator

from . import setup_component, unload_component


async def test_get_value(hass: HomeAssistant, mocked_data, caplog):
    """Test get_value function."""
    config_entry = await setup_component(hass)

    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    assert Decimal(coordinator.get_value(["liveweer", 0, "temp"])) == Decimal(10.5)
    assert "Path ['liveweer', 0, 'temp'] returns a float (value = 10.5)" in caplog.text

    assert coordinator.get_value(["liveweer", 0, "lv"]) == 97
    assert "Path ['liveweer', 0, 'lv'] returns a int (value = 97)" in caplog.text

    assert coordinator.get_value(["liveweer", 0, "plaats"]) == "Purmerend"
    assert (
        "Path ['liveweer', 0, 'plaats'] returns a str (value = Purmerend)"
        in caplog.text
    )

    await unload_component(hass, config_entry)


async def test_get_value_missing_values(hass: HomeAssistant, mocked_data, caplog):
    """Test get_value function with missing values."""
    config_entry = await setup_component(hass)

    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Remove some values.
    del coordinator.data["liveweer"][0]["plaats"]
    del coordinator.data["liveweer"][0]["temp"]
    del coordinator.data["liveweer"][0]["image"]

    assert coordinator.get_value(["liveweer", 0, "plaats"]) is None
    assert (
        "Can't find a value for ['liveweer', 0, 'plaats'] in the API response"
        in caplog.text
    )

    assert coordinator.get_value(["liveweer", 0, "temp"]) is None
    assert (
        "Can't find a value for ['liveweer', 0, 'temp'] in the API response"
        in caplog.text
    )

    # Default value.
    assert coordinator.get_value(["liveweer", 0, "image"], "not_there") == "not_there"
    assert (
        "Can't find a value for ['liveweer', 0, 'image'] in the API response"
        in caplog.text
    )

    await unload_component(hass, config_entry)


@freeze_time("2024-02-14T12:00:00+00:00")
async def test_get_value_datetime(hass: HomeAssistant, mocked_data, caplog):
    """Test get_value_datetime function."""
    config_entry = await setup_component(hass)

    coordinator: KnmiDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Timestamp.
    assert (
        str(coordinator.get_value_datetime(["liveweer", 0, "timestamp"]))
        == "2024-02-14 22:08:03+01:00"
    )
    assert (
        str(coordinator.get_value_datetime(["uur_verw", 0, "timestamp"]))
        == "2024-02-14 23:00:00+01:00"
    )

    # Timestamp, 0 or lower value.
    coordinator.data["liveweer"][0]["wrsch_gts"] = 0
    assert coordinator.get_value_datetime(["liveweer", 0, "wrsch_gts"]) is None

    # Time.
    assert (
        str(coordinator.get_value_datetime(["liveweer", 0, "sup"]))
        == "2024-02-14 07:57:00+01:00"
    )
    assert (
        str(coordinator.get_value_datetime(["liveweer", 0, "sunder"]))
        == "2024-02-14 17:51:00+01:00"
    )

    # Date.
    assert (
        str(coordinator.get_value_datetime(["wk_verw", 0, "dag"]))
        == "2024-02-14 00:00:00+01:00"
    )
    assert (
        str(coordinator.get_value_datetime(["wk_verw", 4, "dag"]))
        == "2024-02-18 00:00:00+01:00"
    )

    # Date and time.
    assert (
        str(coordinator.get_value_datetime(["liveweer", 0, "time"]))
        == "2024-02-14 22:08:03+01:00"
    )

    # Date and time without seconds.
    assert (
        str(coordinator.get_value_datetime(["uur_verw", 0, "uur"]))
        == "2024-02-14 23:00:00+01:00"
    )
    assert (
        str(coordinator.get_value_datetime(["uur_verw", 3, "uur"]))
        == "2024-02-15 02:00:00+01:00"
    )
    assert (
        str(coordinator.get_value_datetime(["uur_verw", 8, "uur"]))
        == "2024-02-15 07:00:00+01:00"
    )

    # Default value.
    assert (
        coordinator.get_value_datetime(["uur_verw", 99, "uur"], "missing") == "missing"
    )

    await unload_component(hass, config_entry)
