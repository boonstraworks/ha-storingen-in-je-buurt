"""De Storingen in je buurt-integratie voor Home Assistant.

Een dun schilletje dat alleen de open API van een "Storingen in je buurt"-hub
leest (`GET /api/disruptions`) en die actuele storingen als sensoren in Home
Assistant beschikbaar maakt. Geen scraping, geen externe afhankelijkheden.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import StoringenCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Zet een configuratie-item op."""
    coordinator = StoringenCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ruim een configuratie-item op."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Herlaad bij gewijzigde opties (postcode / interval)."""
    await hass.config_entries.async_reload(entry.entry_id)
