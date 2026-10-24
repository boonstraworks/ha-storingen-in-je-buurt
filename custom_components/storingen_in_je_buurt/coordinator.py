"""DataUpdateCoordinator: haalt de storingen periodiek bij de hub op."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_POSTCODE,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15


class StoringenCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Beheert het periodiek ophalen van /api/disruptions."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.base_url: str = entry.data[CONF_URL].rstrip("/")
        # Opties hebben voorrang op de oorspronkelijke invoer.
        self.postcode: str = (
            entry.options.get(CONF_POSTCODE, entry.data.get(CONF_POSTCODE, "")) or ""
        ).strip()
        interval = max(
            MIN_SCAN_INTERVAL,
            int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval),
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        url = f"{self.base_url}/api/disruptions"
        params: dict[str, str] = {}
        if self.postcode:
            params["postcode"] = self.postcode

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(url, params=params)
                response.raise_for_status()
                data = await response.json()
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Time-out bij het ophalen van {url}") from err
        except Exception as err:  # noqa: BLE001 - alles netjes als UpdateFailed
            raise UpdateFailed(f"Kon {url} niet ophalen: {err}") from err

        if not isinstance(data, dict) or "disruptions" not in data:
            raise UpdateFailed("Onverwacht antwoord van de hub (geen 'disruptions').")

        return data
