"""Canonical RAM product slug validation and official-source checks."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from app.utils.helpers import slugify

VALID_RAM_MANUFACTURERS = frozenset({
    "corsair",
    "gskill",
    "kingston",
    "crucial",
    "teamgroup",
})

VALID_RAM_MARKET_SEGMENTS = frozenset({
    "desktop",
    "laptop",
    "server",
    "workstation",
})

VALID_RAM_FORM_FACTORS = frozenset({
    "udimm",
    "so-dimm",
    "rdimm",
    "lrdimm",
})

RAM_OFFICIAL_SOURCE_DOMAINS: dict[str, tuple[str, ...]] = {
    "corsair": ("corsair.com",),
    "gskill": ("gskill.com",),
    "kingston": ("kingston.com",),
    "crucial": ("crucial.com", "micron.com"),
    "teamgroup": ("teamgroupinc.com", "teamgroup.com"),
}

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _manufacturer_slug(manufacturer: str) -> str:
    return slugify(manufacturer.replace(".", ""))


def validate_ram_manufacturer(manufacturer: str | None) -> str | None:
    if not manufacturer:
        return "Missing manufacturer"
    if _manufacturer_slug(manufacturer) not in VALID_RAM_MANUFACTURERS:
        return f"Invalid RAM manufacturer '{manufacturer}'"
    return None


def validate_ram_market_segment(segment: str | None) -> str | None:
    if not segment:
        return "Missing market_segment specification"
    if segment.strip().lower() not in VALID_RAM_MARKET_SEGMENTS:
        return f"Invalid RAM market_segment '{segment}'"
    return None


def validate_ram_form_factor(form_factor: str | None) -> str | None:
    if not form_factor:
        return "Missing form_factor specification"
    if form_factor.strip().lower() not in VALID_RAM_FORM_FACTORS:
        return f"Invalid RAM form_factor '{form_factor}'"
    return None


def validate_ram_slug(slug: str | None, manufacturer: str) -> str | None:
    if not slug:
        return "Missing product slug"
    if not _SLUG_PATTERN.match(slug):
        return f"Invalid RAM slug '{slug}'"
    prefix = _manufacturer_slug(manufacturer)
    if not slug.startswith(f"{prefix}-"):
        return (
            f"RAM slug '{slug}' must start with manufacturer prefix "
            f"'{prefix}-'"
        )
    return None


def is_official_ram_source_url(manufacturer: str, url: str) -> bool:
    mfr = _manufacturer_slug(manufacturer)
    domains = RAM_OFFICIAL_SOURCE_DOMAINS.get(mfr, ())
    if not domains:
        return False
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in domains)
