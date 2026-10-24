"""Binary sensor: is er nu een storing in de buurt?"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CATEGORIES, DOMAIN
from .coordinator import StoringenCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: StoringenCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([StoringActiefBinarySensor(coordinator, entry)])


class StoringActiefBinarySensor(
    CoordinatorEntity[StoringenCoordinator], BinarySensorEntity
):
    """Aan zodra er minstens één storing is."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_name = "Storing in de buurt"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: StoringenCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_actief"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="BoonstraWorks",
            model="Storingen in je buurt",
            configuration_url=coordinator.base_url,
        )

    @property
    def _disruptions(self) -> list[dict[str, Any]]:
        data = self.coordinator.data or {}
        items = data.get("disruptions", [])
        return items if isinstance(items, list) else []

    @property
    def is_on(self) -> bool:
        return len(self._disruptions) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        per_categorie = {cat: 0 for cat in CATEGORIES}
        for d in self._disruptions:
            cat = d.get("category", "overig")
            per_categorie[cat] = per_categorie.get(cat, 0) + 1
        return {
            "aantal": len(self._disruptions),
            "per_categorie": per_categorie,
        }
