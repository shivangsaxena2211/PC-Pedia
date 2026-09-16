"""Canonical GPU product slug policy and validation."""

from __future__ import annotations

import re

from app.utils.helpers import slugify

VALID_GPU_MANUFACTURERS = frozenset({"nvidia", "amd", "intel"})

VALID_GPU_FAMILIES: dict[str, frozenset[str]] = {
    "nvidia": frozenset({"geforce", "geforce-gtx", "quadro", "tesla", "rtx-professional"}),
    "amd": frozenset({"radeon", "radeon-rx", "radeon-pro", "instinct"}),
    "intel": frozenset({"arc", "arc-pro", "data-center-gpu"}),
}

VALID_GPU_MARKET_SEGMENTS = frozenset({
    "desktop",
    "mobile",
    "workstation",
    "datacenter",
    "server",
})

GPU_OFFICIAL_SOURCE_DOMAINS: dict[str, tuple[str, ...]] = {
    "nvidia": ("nvidia.com",),
    "amd": ("amd.com",),
    "intel": ("intel.com",),
}

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def gpu_slug_prefix(manufacturer: str, family: str) -> str:
    """Return the required `{manufacturer}-{family}` slug prefix."""
    return f"{slugify(manufacturer)}-{slugify(family)}"


def validate_gpu_manufacturer(manufacturer: str | None) -> str | None:
    if not manufacturer:
        return "Missing manufacturer"
    slug = slugify(manufacturer)
    if slug not in VALID_GPU_MANUFACTURERS:
        return f"Invalid GPU manufacturer '{manufacturer}'"
    return None


def validate_gpu_family(manufacturer: str, family: str | None) -> str | None:
    if not family:
        return "Missing family"
    mfr_slug = slugify(manufacturer)
    family_slug = slugify(family)
    allowed = VALID_GPU_FAMILIES.get(mfr_slug)
    if not allowed:
        return f"Unknown GPU manufacturer '{manufacturer}'"
    if family_slug not in allowed:
        return (
            f"Family '{family}' is not valid for GPU manufacturer "
            f"'{manufacturer}' (allowed: {', '.join(sorted(allowed))})"
        )
    return None


def validate_gpu_slug(slug: str | None, manufacturer: str, family: str) -> str | None:
    if not slug:
        return "Missing product slug"
    if slug != slug.lower():
        return f"Slug '{slug}' must be lowercase"
    if not _SLUG_PATTERN.match(slug):
        return f"Slug '{slug}' must use lowercase letters, digits, and hyphens only"
    prefix = gpu_slug_prefix(manufacturer, family)
    if not slug.startswith(f"{prefix}-"):
        return f"Slug '{slug}' must start with '{prefix}-'"
    model_part = slug[len(prefix) + 1 :]
    if not model_part:
        return f"Slug '{slug}' is missing model identifier after '{prefix}-'"
    return None


def validate_gpu_market_segment(value: str | None) -> str | None:
    if not value:
        return "Missing market_segment specification"
    normalized = value.strip().lower()
    if normalized not in VALID_GPU_MARKET_SEGMENTS:
        segments = ", ".join(sorted(VALID_GPU_MARKET_SEGMENTS))
        return f"Invalid market_segment '{value}' (allowed: {segments})"
    return None


def is_official_gpu_source_url(manufacturer: str, url: str | None) -> bool:
    """Return True when the URL belongs to the manufacturer's official domain."""
    if not url:
        return False
    mfr_slug = slugify(manufacturer)
    domains = GPU_OFFICIAL_SOURCE_DOMAINS.get(mfr_slug, ())
    url_lower = url.lower()
    return any(domain in url_lower for domain in domains)
