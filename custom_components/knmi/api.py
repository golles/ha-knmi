"""KnmiApiClient"""
import asyncio
import logging
import socket

import aiohttp
import async_timeout

from .const import API_ENDPOINT, API_TIMEOUT

_LOGGER: logging.Logger = logging.getLogger(__package__)


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
                    # The API has no proper error handling for a wrong API key.
                    # Instead a 200 with a message is returned, try to detect that here.
                    if "Vraag eerst een API-key op" in await response.text():
                        raise KnmiApiException("Invalid API key")

                    if "Dagelijkse limiet" in await response.text():
                        raise KnmiApiException("Exceeded Daily Limit")

                    data = await response.json()
                    return data.get("liveweer")[0]

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except KnmiApiException as exception:
            _LOGGER.error("Error in API! - %s", exception)
            # Raise to pass on to the user.
            raise exception
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)


class KnmiApiException(Exception):
    """KNMI API Exception class"""
