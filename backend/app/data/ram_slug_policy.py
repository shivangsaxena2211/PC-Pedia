"""Canonical RAM product slug policy for PC Pedia."""

from __future__ import annotations

import re

# Legacy seed/demo slugs mapped to canonical catalog slugs for the same product.
LEGACY_RAM_SLUG_MAP: dict[str, str] = {
    "fury-beast-ddr4-32gb": "kingston-fury-beast-kf432c16bb1k2-32",
}


def _normalize_part(part_number: str) -> str:
    text = part_number.strip().lower()
    text = text.replace("/", "-")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def canonical_ram_slug(manufacturer: str, series: str, part_number: str) -> str:
    """Build deterministic catalog slug including manufacturer part number."""
    mfr = manufacturer.strip().lower().replace(".", "")
    mfr = re.sub(r"[^a-z0-9]+", "-", mfr).strip("-")
    series_slug = re.sub(r"[^a-z0-9]+", "-", series.strip().lower()).strip("-")
    part = _normalize_part(part_number)
    return f"{mfr}-{series_slug}-{part}"


def resolve_canonical_ram_slug(slug: str) -> str:
    return LEGACY_RAM_SLUG_MAP.get(slug, slug)
