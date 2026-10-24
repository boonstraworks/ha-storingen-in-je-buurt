"""Sensoren: één totaalteller + een teller per categorie."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CATEGORIES,
    CATEGORY_ICONS,
    CATEGORY_NAMES,
    DOMAIN,
)
from .coordinator import StoringenCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: StoringenCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [StoringenTotaalSensor(coordinator, entry)]
    entities.extend(
        StoringenCategorieSensor(coordinator, entry, cat) for cat in CATEGORIES
    )
    async_add_entities(entities)


class _BaseSensor(CoordinatorEntity[StoringenCoordinator], SensorEntity):
    """Gedeelde basis: device-info, attribution, eenheid."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_native_unit_of_measurement = "storingen"

    def __init__(self, coordinator: StoringenCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
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


class StoringenTotaalSensor(_BaseSensor):
    """Totaal aantal actuele storingen."""

    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator: StoringenCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_name = "Totaal"
        self._attr_unique_id = f"{entry.entry_id}_totaal"

    @property
    def native_value(self) -> int:
        return len(self._disruptions)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        per_categorie = {cat: 0 for cat in CATEGORIES}
        for d in self._disruptions:
            cat = d.get("category", "overig")
            per_categorie[cat] = per_categorie.get(cat, 0) + 1
        data = self.coordinator.data or {}
        return {
            "bijgewerkt": data.get("generatedAt"),
            "per_categorie": per_categorie,
            "storingen": [
                {
                    k: d.get(k)
                    for k in (
                        "category",
                        "place",
                        "description",
                        "status",
                        "sourceLabel",
                        "unconfirmed",
                    )
                }
                for d in self._disruptions[:25]
            ],
        }


class StoringenCategorieSensor(_BaseSensor):
    """Aantal storingen in één categorie."""

    def __init__(
        self,
        coordinator: StoringenCoordinator,
        entry: ConfigEntry,
        categorie: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._categorie = categorie
        self._attr_name = CATEGORY_NAMES.get(categorie, categorie.title())
        self._attr_icon = CATEGORY_ICONS.get(categorie, "mdi:alert")
        self._attr_unique_id = f"{entry.entry_id}_{categorie}"

    @property
    def _eigen(self) -> list[dict[str, Any]]:
        return [d for d in self._disruptions if d.get("category") == self._categorie]

    @property
    def native_value(self) -> int:
        return len(self._eigen)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "storingen": [
                {
                    k: d.get(k)
                    for k in (
                        "place",
                        "description",
                        "status",
                        "postalCodes",
                        "unconfirmed",
                        "reportCount",
                    )
                }
                for d in self._eigen[:25]
            ],
        }
