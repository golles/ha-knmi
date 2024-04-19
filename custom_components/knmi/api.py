"""KnmiApiClient"""

import asyncio
import json
import logging
import socket

import aiohttp

from .const import API_ENDPOINT, API_TIMEOUT

_LOGGER: logging.Logger = logging.getLogger(__package__)


class KnmiApiClientError(Exception):
    """Exception to indicate a general API error."""


class KnmiApiClientCommunicationError(KnmiApiClientError):
    """Exception to indicate a communication error."""


class KnmiApiClientApiKeyError(KnmiApiClientError):
    """Exception to indicate an api key error."""


class KnmiApiRateLimitError(KnmiApiClientError):
    """Exception to indicate a rate limit error."""


class KnmiApiClient:
    """KNMI API wrapper"""

    response_text = None

    def __init__(
        self,
        api_key: str,
        latitude: str,
        longitude: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self._session = session

    async def get_response_text(self) -> str:
        """Get API response text"""
        async with asyncio.timeout(API_TIMEOUT):
            response = await self._session.get(
                API_ENDPOINT.format(self.api_key, self.latitude, self.longitude)
            )

            return await response.text()

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        try:
            self.response_text = await self.get_response_text()

            # The API has no proper error handling for a wrong API key or rate limit.
            # Instead a 200 with a message is returned, try to detect that here.
            if "Vraag eerst een API-key op" in self.response_text:
                raise KnmiApiClientApiKeyError("The given API key is invalid")

            if "Dagelijkse limiet" in self.response_text:
                raise KnmiApiRateLimitError(
                    "API key daily limit exceeded, try again tomorrow"
                )

            # The API has an ongoing issue due to invalid JSON response.
            # Where a null value of a number field is set to _ (without quotes).
            # Here we fix the JSON by setting the value to null.
            # More info: https://github.com/golles/ha-knmi/issues/130
            if '": _,' in self.response_text:
                _LOGGER.debug("Detected invalid JSON, attempting to fix that...")
                return json.loads(self.response_text.replace('": _,', '": null,'))

            return json.loads(self.response_text)

        except asyncio.TimeoutError as exception:
            raise KnmiApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise KnmiApiClientCommunicationError(
                "Error fetching information",
            ) from exception
