"""Canonical CPU product slug policy for PC Pedia."""

from __future__ import annotations

import re


# Legacy seed/demo slugs mapped to canonical catalog slugs for the same physical CPU.
LEGACY_CPU_SLUG_MAP: dict[str, str] = {
    "core-i9-14900k": "intel-core-i9-14900k",
    "core-i7-14700k": "intel-core-i7-14700k",
    "ryzen-7-7800x3d": "amd-ryzen-7-7800x3d",
    "ryzen-9-9950x": "amd-ryzen-9-9950x",
}


def canonical_cpu_slug(manufacturer: str, product_name: str) -> str:
    """Build deterministic catalog slug: intel-core-i9-14900k, amd-ryzen-7-7800x3d."""
    mfr = manufacturer.strip().lower()
    name = product_name.lower()
    name = re.sub(r"[™®]", "", name)
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    if name.startswith(f"{mfr}-"):
        return name
    return f"{mfr}-{name}"


def resolve_canonical_slug(slug: str) -> str:
    return LEGACY_CPU_SLUG_MAP.get(slug, slug)
