"""Global fixtures for knmi integration."""

from collections.abc import Generator
from unittest.mock import PropertyMock, patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.knmi.api import KnmiApiClientApiKeyError, KnmiApiClientCommunicationError, KnmiApiRateLimitError


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Generator) -> Generator[None]:
    """Enable custom integrations."""
    return enable_custom_integrations


@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture() -> Generator[None]:
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


@pytest.fixture(name="enable_all_entities", autouse=True)
def fixture_enable_all_entities() -> Generator[None]:
    """Make sure all entities are enabled."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        PropertyMock(return_value=True),
    ):
        yield


@pytest.fixture(name="mocked_data")
def mocked_data_fixture(request: pytest.FixtureRequest) -> Generator[None]:
    """Use mocked data in the integration."""
    json_file = "response.json"
    fixture = request.node.get_closest_marker("response_json_file")

    if fixture is not None:
        json_file = fixture.args[0]

    with patch(
        "custom_components.knmi.KnmiApiClient.get_response_text",
        return_value=load_fixture(json_file),
    ):
        yield


@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture() -> Generator[None]:
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        side_effect=KnmiApiClientCommunicationError,
    ):
        yield


@pytest.fixture(
    name="config_flow_exceptions",
    params=[
        KnmiApiClientCommunicationError,
        KnmiApiClientApiKeyError,
        KnmiApiRateLimitError,
    ],
)
def config_flow_exceptions_fixture(request: pytest.FixtureRequest) -> Generator[None]:
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        side_effect=request.param,
    ):
        yield
