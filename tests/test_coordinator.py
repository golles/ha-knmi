"""Test for data update coordinator."""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.knmi.const import DOMAIN
from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator

from . import get_mock_config_data, get_mock_config_entry


async def test_async_update_data_success(hass: HomeAssistant, mock_weerlive_client: AsyncMock) -> None:
    """Test successful data update."""
    coordinator = KnmiDataUpdateCoordinator(
        hass=hass,
        client=mock_weerlive_client,
        scan_interval=timedelta(minutes=5),
    )
    coordinator.config_entry = get_mock_config_entry()
    result = await coordinator._async_update_data()  # pylint: disable=protected-access # noqa: SLF001
    assert isinstance(result, AsyncMock)
    mock_weerlive_client.latitude_longitude.assert_awaited_once_with(
        latitude=get_mock_config_data()["latitude"],
        longitude=get_mock_config_data()["longitude"],
    )


@pytest.mark.parametrize("missing_key", ["latitude", "longitude"])
async def test_async_update_data_missing_coordinates(hass: HomeAssistant, mock_weerlive_client: AsyncMock, missing_key: str) -> None:
    """Test missing coordinates."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry",
        data={
            "latitude": 52.354 if missing_key != "latitude" else None,
            "longitude": 4.763 if missing_key != "longitude" else None,
        },
    )
    coordinator = KnmiDataUpdateCoordinator(
        hass=hass,
        client=mock_weerlive_client,
        scan_interval=timedelta(minutes=5),
    )
    coordinator.config_entry = config_entry
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()  # pylint: disable=protected-access # noqa: SLF001


async def test_async_update_data_api_failure(hass: HomeAssistant, mock_weerlive_client: AsyncMock) -> None:
    """Test API failure."""
    mock_weerlive_client.latitude_longitude.side_effect = Exception("API error")
    coordinator = KnmiDataUpdateCoordinator(
        hass=hass,
        client=mock_weerlive_client,
        scan_interval=timedelta(minutes=5),
    )
    coordinator.config_entry = get_mock_config_entry()
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()  # pylint: disable=protected-access # noqa: SLF001
