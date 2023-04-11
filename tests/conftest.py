"""Global fixtures for knmi integration."""
# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# pytest_homeassistant_custom_component provides some fixtures that are provided by
# Home Assistant core. You can find those fixture definitions here:
# https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/master/pytest_homeassistant_custom_component/common.py
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)
import json
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.knmi.api import (
    KnmiApiClientApiKeyError,
    KnmiApiClientCommunicationError,
    KnmiApiRateLimitError,
)

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture, when used, will have the mocked values from response.json loaded in the integration.
@pytest.fixture(name="mocked_data")
def mocked_data_fixture():
    """Skip calls to get data from API."""
    data = json.loads(load_fixture("response.json"))

    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        return_value=data,
    ):
        yield


# This fixture, when used, will have the mocked values from response.json loaded in the integration.
# As an addition, the alarm and alarmtxt are set.
@pytest.fixture(name="mocked_data_alarm")
def mocked_data_alarm_fixture():
    """Skip calls to get data from API."""
    data = json.loads(load_fixture("response.json"))

    data["alarm"] = "1"
    data["alarmtxt"] = "Code geel in bijna hele land vanwege gladheid"

    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        return_value=data,
    ):
        yield


# This fixture, when used, will have the mocked values from response.json loaded in the integration.
# As an addition, plaats has been removed and temp has been set to an empty value.
@pytest.fixture(name="mocked_data_empty_values")
def mocked_data_empty_values_fixture():
    """Skip calls to get data from API."""
    data = json.loads(load_fixture("response.json"))

    del data["plaats"]
    data["temp"] = ""

    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        return_value=data,
    ):
        yield


# In this fixture, we raise an KnmiApiClientCommunicationError in async_get_data.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        side_effect=KnmiApiClientCommunicationError,
    ):
        yield


# In this fixture, we raise all exceptions in async_get_data.
@pytest.fixture(
    name="config_flow_exceptions",
    params=[
        KnmiApiClientCommunicationError,
        KnmiApiClientApiKeyError,
        KnmiApiRateLimitError,
    ],
)
def config_flow_exceptions_fixture(request):
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.knmi.KnmiApiClient.async_get_data",
        side_effect=request.param,
    ):
        yield


# See https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/issues/153
@pytest.fixture(autouse=True)
def expected_lingering_timers() -> bool:
    """Temporary ability to bypass test failures.
    Parametrize to True to bypass the pytest failure.
    @pytest.mark.parametrize("expected_lingering_timers", [True])
    This should be removed when all lingering timers have been cleaned up.
    """
    return True
