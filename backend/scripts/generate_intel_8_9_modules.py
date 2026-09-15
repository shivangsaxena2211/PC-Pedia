"""Generate verified_intel_8th_gen.py and verified_intel_9th_gen.py from ARK fetch output."""

from __future__ import annotations

import json
import re
from pathlib import Path

ARK_DATA = Path(__file__).resolve().parent / "ark_desktop_8_9.json"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "catalog" / "cpu"
VERIFIED_DATE = "2026-09-15"

COMMON_9 = {
    "socket": "LGA 1151",
    "architecture": "Coffee Lake Refresh",
    "microarchitecture": "Coffee Lake Refresh",
    "process_node": "14 nm",
    "market_segment": "Desktop",
    "product_family": "Core",
    "generation": "9th Generation",
    "memory_channels": "2",
    "max_memory": "128",
    "memory_type": "DDR4-2666",
    "pcie_version": "3.0",
    "ecc_support": "false",
    "virtualization": "true",
    "aes": "true",
    "avx2": "true",
    "intel_turbo_boost": "true",
}

COMMON_8 = {
    "socket": "LGA 1151",
    "architecture": "Coffee Lake",
    "microarchitecture": "Coffee Lake",
    "process_node": "14 nm",
    "market_segment": "Desktop",
    "product_family": "Core",
    "generation": "8th Generation",
    "memory_channels": "2",
    "max_memory": "128",
    "memory_type": "DDR4-2666",
    "pcie_version": "3.0",
    "ecc_support": "false",
    "virtualization": "true",
    "aes": "true",
    "avx2": "true",
    "intel_turbo_boost": "true",
}


def _parse_ghz(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"([\d.]+)\s*GHz", value)
    return match.group(1) if match else None


def _parse_mhz(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"([\d.]+)\s*GHz", value)
    if match:
        return str(int(float(match.group(1)) * 1000))
    match = re.search(r"(\d+)\s*MHz", value)
    return match.group(1) if match else None


def _parse_w(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"(\d+)\s*W", value)
    return match.group(1) if match else None


def _parse_mb(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"([\d.]+)\s*MB", value)
    return match.group(1) if match else None


def _field(raw: dict, *prefixes: str) -> str | None:
    for prefix in prefixes:
        for key, value in raw.items():
            if key.startswith(prefix):
                return value
    return None


def _release_date(raw: dict, fallback: str | None) -> str:
    launch = _field(raw, "Launch Date")
    if launch and re.match(r"Q(\d)'(\d{2})", launch):
        quarter, year_suffix = re.match(r"Q(\d)'(\d{2})", launch).groups()
        year = 2000 + int(year_suffix)
        month = {"1": "01", "2": "04", "3": "07", "4": "10"}[quarter]
        return f"{year}-{month}-01"
    return fallback or "2018-10-01"


def _pcie_lanes(raw: dict) -> str:
    value = _field(raw, "PCI Express Configurations")
    if value:
        match = re.search(r"x(\d+)", value)
        if match:
            return match.group(1)
        match = re.search(r"(\d+)\s*Lanes", value, re.I)
        if match:
            return match.group(1)
    return "16"


def _graphics_model(raw: dict) -> str | None:
    value = _field(raw, "GPU Name", "Processor Graphics")
    if not value:
        return None
    return value.replace("Intel® ", "Intel ").replace("®", "").strip()


def _normalize_model(model: str) -> str:
    normalized = model.strip().lower()
    match = re.match(r"(i[3579]-\d{4})([a-z]*)", normalized)
    if not match:
        return normalized
    return match.group(1) + match.group(2).upper()


def convert_entry(entry: dict, generation: str) -> dict:
    raw = entry.get("raw_fields", {})
    proc = _field(raw, "Processor Number")
    model = _normalize_model(proc or entry["model"])
    specs = dict(COMMON_9 if generation == "9th" else COMMON_8)

    specs["cores"] = entry["specs"]["cores"]
    specs["threads"] = entry["specs"]["threads"]
    base_clock = _parse_ghz(_field(raw, "Processor Base Frequency")) or entry["specs"].get("base_clock")
    boost_clock = _parse_ghz(_field(raw, "Max Turbo Frequency")) or entry["specs"].get("boost_clock")
    if base_clock:
        specs["base_clock"] = base_clock
    if boost_clock:
        specs["boost_clock"] = boost_clock
    specs["l3_cache"] = _parse_mb(_field(raw, "Cache", "Intel® Smart Cache")) or entry["specs"].get("l3_cache")
    specs["tdp"] = _parse_w(_field(raw, "TDP")) or entry["specs"].get("tdp")

    mem_type = _field(raw, "Memory Types")
    if mem_type:
        specs["memory_type"] = mem_type
        speed = re.search(r"-(\d+)", mem_type)
        if speed:
            specs["max_memory_speed"] = speed.group(1)

    max_mem = _field(raw, "Max Memory Size")
    if max_mem:
        match = re.search(r"(\d+)", max_mem)
        if match:
            specs["max_memory"] = match.group(1)

    pcie_version = _field(raw, "PCI Express Revision")
    if pcie_version:
        match = re.search(r"(\d+\.\d+)", pcie_version)
        if match:
            specs["pcie_version"] = match.group(1)

    specs["pcie_lanes"] = _pcie_lanes(raw)

    graphics = _graphics_model(raw)
    has_igpu = graphics and "none" not in graphics.lower()
    specs["integrated_graphics"] = "true" if has_igpu else "false"
    if has_igpu:
        specs["graphics_model"] = graphics
        base = _parse_mhz(_field(raw, "Graphics Base Frequency"))
        max_clock = _parse_mhz(_field(raw, "Graphics Max Dynamic Frequency"))
        if base:
            specs["graphics_base_clock"] = base
        if max_clock:
            specs["graphics_max_clock"] = max_clock

    specs["overclocking_support"] = "true" if model.endswith("K") else "false"

    turbo_max = _parse_ghz(_field(raw, "Intel® Turbo Boost Max Technology 3.0 Frequency"))
    if turbo_max:
        specs["turbo_boost_max"] = "true"

    popular = model in {
        "i9-9900K", "i7-9700K", "i5-9600K",
        "i7-8700K", "i5-8600K",
    }

    cleaned_specs = {key: value for key, value in specs.items() if value not in (None, "", "None")}
    return {
        "model": model,
        "sku": entry["sku"],
        "release_date": _release_date(raw, entry.get("release_date")),
        **({"is_popular": True} if popular else {}),
        "specs": cleaned_specs,
    }


def render_module(name: str, var_name: str, entries: list[dict]) -> str:
    lines = [
        f'"""Verified Intel Core {name} desktop CPU specifications (source: Intel ARK)."""',
        "",
        f'VERIFIED_DATE = "{VERIFIED_DATE}"',
        "",
        f"{var_name} = [",
    ]
    for entry in entries:
        lines.append("    {")
        lines.append(f'        "model": "{entry["model"]}",')
        lines.append(f'        "sku": {entry["sku"]},')
        lines.append(f'        "release_date": "{entry["release_date"]}",')
        if entry.get("is_popular"):
            lines.append('        "is_popular": True,')
        lines.append('        "specs": {')
        for key, value in entry["specs"].items():
            lines.append(f'            "{key}": "{value}",')
        lines.append("        },")
        lines.append("    },")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def main():
    data = json.loads(ARK_DATA.read_text(encoding="utf-8"))
    gen9 = sorted(
        [convert_entry(e, "9th") for e in data if "9th" in e["collection"]],
        key=lambda x: x["model"],
    )
    gen8 = sorted(
        [convert_entry(e, "8th") for e in data if "8th" in e["collection"]],
        key=lambda x: x["model"],
    )
    (OUT_DIR / "verified_intel_9th_gen.py").write_text(
        render_module("9th Gen", "INTEL_9TH_GEN_DESKTOP", gen9),
        encoding="utf-8",
    )
    (OUT_DIR / "verified_intel_8th_gen.py").write_text(
        render_module("8th Gen", "INTEL_8TH_GEN_DESKTOP", gen8),
        encoding="utf-8",
    )
    print(f"Wrote {len(gen9)} 9th gen and {len(gen8)} 8th gen entries")


if __name__ == "__main__":
    main()
