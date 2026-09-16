"""Validation helpers for hardware catalog JSON records."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from app.catalog.gpu_slug import (
    is_official_gpu_source_url,
    validate_gpu_family,
    validate_gpu_manufacturer,
    validate_gpu_market_segment,
    validate_gpu_slug,
)
from app.data.taxonomy_rules import validate_family_for_manufacturer
from app.utils.helpers import slugify

CPU_ALLOWED_SPEC_KEYS = {
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

GPU_ALLOWED_SPEC_KEYS = {
    "architecture", "gpu_die", "codename", "generation", "product_family",
    "market_segment", "launch_msrp", "process_node", "compute_units", "shader_units",
    "cuda_cores", "stream_processors", "xe_cores", "rt_cores", "tensor_cores",
    "ray_accelerators", "xmx_engines", "ray_tracing_units", "base_clock", "boost_clock",
    "game_clock", "memory_clock", "vram_capacity", "vram_type", "memory_bus_width",
    "memory_speed", "memory_bandwidth", "tdp", "tbp", "board_power", "recommended_psu",
    "pci_express", "display_outputs", "maximum_displays", "slot_width", "length",
    "height", "power_connectors",
}

# Backward-compatible alias used by the CPU catalog builder.
ALLOWED_SPEC_KEYS = CPU_ALLOWED_SPEC_KEYS

GPU_INTEGER_SPEC_KEYS = {
    "compute_units", "shader_units", "cuda_cores", "stream_processors", "xe_cores",
    "rt_cores", "tensor_cores", "ray_accelerators", "xmx_engines", "ray_tracing_units",
    "vram_capacity", "memory_bus_width", "memory_speed", "tdp", "tbp", "board_power",
    "recommended_psu", "maximum_displays",
}

GPU_DECIMAL_SPEC_KEYS = {
    "launch_msrp", "base_clock", "boost_clock", "game_clock", "memory_clock",
    "memory_bandwidth", "length", "height",
}

INVALID_SOURCE_PATTERNS = (
    re.compile(r"^https?://example\.com", re.I),
    re.compile(r"^https?://\.\.\.", re.I),
    re.compile(r"^https?://$", re.I),
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bTBD\b", re.I),
    re.compile(r"\bplaceholder\b", re.I),
)


def get_allowed_spec_keys(category_slug: str) -> set[str]:
    if category_slug == "gpu":
        return GPU_ALLOWED_SPEC_KEYS
    return CPU_ALLOWED_SPEC_KEYS


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


def _spec_value_from_record(record: dict, key: str) -> str | None:
    for spec in record.get("specifications") or []:
        if spec.get("key") == key:
            value = spec.get("value")
            return str(value) if value is not None else None
    return None


def _validate_numeric_spec_value(key: str, value: str, category_slug: str) -> str | None:
    if category_slug != "gpu":
        return None
    if key in GPU_INTEGER_SPEC_KEYS:
        try:
            parsed = int(str(value).strip())
        except (TypeError, ValueError):
            return f"Specification '{key}' must be an integer"
        if parsed < 0:
            return f"Specification '{key}' must be non-negative"
    elif key in GPU_DECIMAL_SPEC_KEYS:
        try:
            parsed = float(str(value).strip())
        except (TypeError, ValueError):
            return f"Specification '{key}' must be a number"
        if parsed < 0:
            return f"Specification '{key}' must be non-negative"
    return None


def validate_catalog_record(record: dict, *, index: int | None = None) -> list[str]:
    """Return validation error messages for a catalog record."""
    errors: list[str] = []
    prefix = f"Record {index}: " if index is not None else ""

    if not isinstance(record, dict):
        return [f"{prefix}Record must be an object"]

    category = slugify(record.get("category", "cpu"))
    allowed_keys = get_allowed_spec_keys(category)

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

    if category == "gpu":
        if manufacturer:
            mfr_error = validate_gpu_manufacturer(manufacturer)
            if mfr_error:
                errors.append(f"{prefix}{mfr_error}")
            if family:
                family_error = validate_gpu_family(manufacturer, family)
                if family_error:
                    errors.append(f"{prefix}{family_error}")
            if slug and family and manufacturer:
                slug_error = validate_gpu_slug(slug, manufacturer, family)
                if slug_error:
                    errors.append(f"{prefix}{slug_error}")
            if manufacturer and source.get("url") and is_valid_source_url(source.get("url")):
                if not is_official_gpu_source_url(manufacturer, source.get("url")):
                    errors.append(
                        f"{prefix}GPU source URL must be an official manufacturer source "
                        f"for '{manufacturer}'"
                    )
        segment_error = validate_gpu_market_segment(
            _spec_value_from_record(record, "market_segment")
        )
        if segment_error:
            errors.append(f"{prefix}{segment_error}")
    elif manufacturer and family:
        family_error = validate_family_for_manufacturer(
            slugify(manufacturer), category, family
        )
        if family_error:
            errors.append(f"{prefix}{family_error}")

    for spec in record.get("specifications") or []:
        key = spec.get("key")
        if key not in allowed_keys:
            errors.append(f"{prefix}Invalid specification key '{key}'")
            continue
        value = spec.get("value")
        if value in (None, ""):
            errors.append(f"{prefix}Specification '{key}' has empty value")
            continue
        numeric_error = _validate_numeric_spec_value(key, str(value), category)
        if numeric_error:
            errors.append(f"{prefix}{numeric_error}")

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
