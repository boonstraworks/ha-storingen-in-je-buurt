"""Configuratiestroom: hub-URL + optionele postcode."""

from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_POSTCODE,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)


def _normalize_url(raw: str) -> str:
    url = raw.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return url


async def _test_hub(hass, url: str) -> None:
    """Controleer of de hub bereikbaar is en antwoordt met status 'ok'."""
    session = async_get_clientsession(hass)
    async with asyncio.timeout(15):
        resp = await session.get(f"{url}/api/health")
        resp.raise_for_status()
        data = await resp.json()
    if not isinstance(data, dict) or data.get("status") != "ok":
        raise ValueError("unexpected_response")


class StoringenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Beheert het toevoegen van een hub."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            url = _normalize_url(user_input[CONF_URL])
            postcode = (user_input.get(CONF_POSTCODE) or "").strip()
            try:
                await _test_hub(self.hass, url)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{url}|{postcode}")
                self._abort_if_unique_id_configured()
                title = (
                    f"Storingen rond {postcode}"
                    if postcode
                    else "Storingen in Nederland"
                )
                return self.async_create_entry(
                    title=title,
                    data={CONF_URL: url, CONF_POSTCODE: postcode},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_URL): str,
                vol.Optional(CONF_POSTCODE, default=""): str,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return StoringenOptionsFlow(config_entry)


class StoringenOptionsFlow(OptionsFlow):
    """Opties: postcode en pollinterval aanpassen zonder opnieuw toevoegen."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_pc = self._entry.options.get(
            CONF_POSTCODE, self._entry.data.get(CONF_POSTCODE, "")
        )
        current_interval = self._entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_POSTCODE, default=current_pc): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=current_interval
                ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
