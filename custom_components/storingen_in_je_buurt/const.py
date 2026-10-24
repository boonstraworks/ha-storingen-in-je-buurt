"""Constanten voor de Storingen in je buurt-integratie."""

from __future__ import annotations

DOMAIN = "storingen_in_je_buurt"

CONF_URL = "url"
CONF_POSTCODE = "postcode"
CONF_SCAN_INTERVAL = "scan_interval"

# Standaard-pollinterval in minuten. De hub cachet zijn bronnen al, dus vaker
# pollen heeft weinig zin.
DEFAULT_SCAN_INTERVAL = 5
MIN_SCAN_INTERVAL = 1

PLATFORMS = ["binary_sensor", "sensor"]

ATTRIBUTION = "Gegevens via Storingen in je buurt (BoonstraWorks)"

# De categorieën zoals de API ze teruggeeft, in vaste volgorde.
CATEGORIES = [
    "stroom",
    "gas",
    "water",
    "internet",
    "telefonie",
    "spoor",
    "weg",
    "weer",
    "overig",
]

CATEGORY_NAMES = {
    "stroom": "Stroom",
    "gas": "Gas",
    "water": "Water",
    "internet": "Internet",
    "telefonie": "Telefonie",
    "spoor": "Spoor",
    "weg": "Weg",
    "weer": "Weer",
    "overig": "Overig",
}

CATEGORY_ICONS = {
    "stroom": "mdi:flash",
    "gas": "mdi:fire",
    "water": "mdi:water",
    "internet": "mdi:wifi",
    "telefonie": "mdi:phone",
    "spoor": "mdi:train",
    "weg": "mdi:road-variant",
    "weer": "mdi:weather-partly-cloudy",
    "overig": "mdi:alert",
}
