"""Global fixtures for the custom component."""

from collections.abc import Generator
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from weerlive import Response, WeerliveApi


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Generator) -> Generator[None]:
    """Enable custom integrations."""
    return enable_custom_integrations


@pytest.fixture(name="enable_all_entities", autouse=True)
def fixture_enable_all_entities() -> Generator[None]:
    """Make sure all entities are enabled."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        PropertyMock(return_value=True),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_async_get_clientsession() -> Generator[None]:
    """Mock async_get_clientsession to avoid aiohttp client session issues in tests."""
    with (
        patch("custom_components.knmi.async_get_clientsession"),
        patch("custom_components.knmi.config_flow.async_get_clientsession"),
    ):
        yield


@pytest.fixture(autouse=True, name="mock_weerlive_client")
def fixture_mock_weerlive_client() -> Generator[AsyncMock]:
    """Auto-patch WeerliveApi in all tests and return the mock for configuration."""
    mock_client = AsyncMock(spec=WeerliveApi)
    mock_client_class = Mock(return_value=mock_client)

    with (
        patch("custom_components.knmi.WeerliveApi", mock_client_class),
        patch("custom_components.knmi.config_flow.WeerliveApi", mock_client_class),
    ):
        yield mock_client


@pytest.fixture(name="mocked_data")
def fixture_mocked_data(request: pytest.FixtureRequest, mock_weerlive_client: AsyncMock) -> None:
    """Fixture for mocking a response with a configurable JSON file."""
    json_file = getattr(request, "param", "response.json")
    response_json = load_fixture(json_file)
    mock_response = Response.from_json(response_json)
    mock_weerlive_client.latitude_longitude.return_value = mock_response
