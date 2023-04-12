"""KnmiApiClient"""
import asyncio
import socket

import aiohttp
import async_timeout

from .const import API_ENDPOINT, API_TIMEOUT


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

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        url = API_ENDPOINT.format(self.api_key, self.latitude, self.longitude)
        return await self.api_wrapper("get", url)

    async def api_wrapper(self, method: str, url: str) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                if method == "get":
                    response = await self._session.get(url)
                    response_text = await response.text()

                    # The API has no proper error handling for a wrong API key or rate limit.
                    # Instead a 200 with a message is returned, try to detect that here.
                    if "Vraag eerst een API-key op" in response_text:
                        raise KnmiApiClientApiKeyError("The given API key is invalid")

                    if "Dagelijkse limiet" in response_text:
                        raise KnmiApiRateLimitError(
                            "API key daily limit exceeded, try again tomorrow"
                        )

                    data = await response.json()
                    return data.get("liveweer")[0]

        except asyncio.TimeoutError as exception:
            raise KnmiApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise KnmiApiClientCommunicationError(
                "Error fetching information",
            ) from exception
