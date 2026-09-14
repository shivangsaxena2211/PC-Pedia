"""Validation helpers for hardware catalog JSON records."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from app.data.taxonomy_rules import validate_family_for_manufacturer
from app.utils.helpers import slugify

ALLOWED_SPEC_KEYS = {
    "architecture", "microarchitecture", "process_node", "market_segment",
    "product_family", "generation", "socket", "cores", "p_cores", "e_cores",
    "threads", "core_complexes", "smt", "base_clock", "p_core_base_clock",
    "p_core_boost_clock", "e_core_base_clock", "e_core_boost_clock", "boost_clock",
    "l1_cache", "l2_cache", "l3_cache", "v_cache", "tdp", "processor_base_power",
    "max_turbo_power", "ppt", "package_power", "memory_type", "memory_channels",
    "max_memory", "max_memory_speed", "ecc_support", "pcie_version", "pcie_lanes",
    "integrated_graphics", "graphics_model", "graphics_base_clock", "graphics_max_clock",
    "overclocking_support", "virtualization", "aes", "avx", "avx2", "avx512",
    "precision_boost", "intel_turbo_boost", "turbo_boost_max",
}

INVALID_SOURCE_PATTERNS = (
    re.compile(r"^https?://example\.com", re.I),
    re.compile(r"^https?://\.\.\.", re.I),
    re.compile(r"^https?://$", re.I),
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bTBD\b", re.I),
    re.compile(r"\bplaceholder\b", re.I),
)


def is_valid_source_url(url: str | None) -> bool:
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return False
    parsed = urlparse(url)
    if not parsed.netloc or "." not in parsed.netloc:
        return False
    return not any(pattern.search(url) for pattern in INVALID_SOURCE_PATTERNS)


def validate_catalog_record(record: dict, *, index: int | None = None) -> list[str]:
    """Return validation error messages for a catalog record."""
    errors: list[str] = []
    prefix = f"Record {index}: " if index is not None else ""

    if not isinstance(record, dict):
        return [f"{prefix}Record must be an object"]

    manufacturer = record.get("manufacturer")
    if not manufacturer:
        errors.append(f"{prefix}Missing manufacturer")

    product = record.get("product") or {}
    name = product.get("name")
    slug = product.get("slug")
    if not name:
        errors.append(f"{prefix}Missing product name")
    if not slug:
        errors.append(f"{prefix}Missing product slug")

    source = record.get("source") or {}
    if not source.get("name"):
        errors.append(f"{prefix}Missing source name")
    if not is_valid_source_url(source.get("url")):
        errors.append(f"{prefix}Invalid or missing source URL")

    family = record.get("family")
    category = slugify(record.get("category", "cpu"))
    if manufacturer and family:
        family_error = validate_family_for_manufacturer(
            slugify(manufacturer), category, family
        )
        if family_error:
            errors.append(f"{prefix}{family_error}")

    for spec in record.get("specifications") or []:
        key = spec.get("key")
        if key not in ALLOWED_SPEC_KEYS:
            errors.append(f"{prefix}Invalid specification key '{key}'")
        if spec.get("value") in (None, ""):
            errors.append(f"{prefix}Specification '{key}' has empty value")

    return errors


def validate_catalog_records(records: list[dict]) -> tuple[list[str], list[str]]:
    """Validate records and detect duplicate slugs within the batch."""
    errors: list[str] = []
    warnings: list[str] = []
    seen_slugs: dict[str, int] = {}

    for idx, record in enumerate(records, start=1):
        errors.extend(validate_catalog_record(record, index=idx))
        slug = (record.get("product") or {}).get("slug")
        if slug:
            if slug in seen_slugs:
                errors.append(
                    f"Record {idx}: Duplicate slug '{slug}' (also in record {seen_slugs[slug]})"
                )
            else:
                seen_slugs[slug] = idx

    return errors, warnings
