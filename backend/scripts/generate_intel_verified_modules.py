"""Generate verified_intel_*_gen.py modules from ARK fetch output."""

from __future__ import annotations

import json
import re
from pathlib import Path

ARK_DATA = Path(__file__).resolve().parent / "ark_desktop_10_11.json"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "catalog" / "cpu"

COMMON_11 = {
    "socket": "LGA 1200",
    "architecture": "Rocket Lake",
    "microarchitecture": "Rocket Lake",
    "process_node": "14 nm",
    "market_segment": "Desktop",
    "product_family": "Core",
    "generation": "11th Generation",
    "memory_channels": "2",
    "max_memory": "128",
    "memory_type": "DDR4-3200",
    "pcie_version": "4.0",
    "pcie_lanes": "20",
    "ecc_support": "false",
    "virtualization": "true",
    "aes": "true",
    "avx2": "true",
    "intel_turbo_boost": "true",
}

COMMON_10 = {
    "socket": "LGA 1200",
    "architecture": "Comet Lake",
    "microarchitecture": "Comet Lake",
    "process_node": "14 nm",
    "market_segment": "Desktop",
    "product_family": "Core",
    "generation": "10th Generation",
    "memory_channels": "2",
    "max_memory": "128",
    "memory_type": "DDR4-2933",
    "pcie_version": "3.0",
    "pcie_lanes": "16",
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
    return fallback or "2020-04-01"


def _max_turbo_power(raw: dict) -> str | None:
    for key, value in raw.items():
        if "Maximum Turbo Power" in key:
            return _parse_w(value)
    return None


def _pcie_lanes(raw: dict, generation: str) -> str:
    value = _field(raw, "PCI Express Configurations")
    if value:
        match = re.search(r"x(\d+)", value)
        if match:
            return match.group(1)
        match = re.search(r"(\d+)\s*Lanes", value, re.I)
        if match:
            return match.group(1)
    return "20" if generation == "11th" else "16"


def _graphics_max_clock(raw: dict) -> str | None:
    return _parse_mhz(_field(raw, "Graphics Max Dynamic Frequency"))


def _graphics_model(raw: dict) -> str | None:
    value = _field(raw, "GPU Name", "Processor Graphics")
    if not value:
        return None
    return value.replace("Intel® ", "Intel ").replace("®", "").strip()


def _normalize_model(model: str) -> str:
    normalized = model.strip().lower()
    match = re.match(r"(i[3579]-\d{5})([a-z]*)", normalized)
    if not match:
        return normalized
    return match.group(1) + match.group(2).upper()


def convert_entry(entry: dict, generation: str) -> dict:
    raw = entry.get("raw_fields", {})
    proc = _field(raw, "Processor Number")
    model = _normalize_model(proc or entry["model"])
    specs = dict(COMMON_11 if generation == "11th" else COMMON_10)

    specs["cores"] = entry["specs"]["cores"]
    specs["threads"] = entry["specs"]["threads"]
    specs["base_clock"] = _parse_ghz(_field(raw, "Processor Base Frequency")) or entry["specs"].get("base_clock")
    specs["boost_clock"] = _parse_ghz(_field(raw, "Max Turbo Frequency", "Intel® Thermal Velocity Boost Frequency")) or entry["specs"].get("boost_clock")
    specs["l3_cache"] = _parse_mb(_field(raw, "Cache")) or entry["specs"].get("l3_cache")
    specs["tdp"] = _parse_w(_field(raw, "TDP")) or entry["specs"].get("tdp")

    mem_type = _field(raw, "Memory Types")
    if mem_type:
        specs["memory_type"] = mem_type
        speed = re.search(r"-(\d+)", mem_type)
        if speed:
            specs["max_memory_speed"] = speed.group(1)

    turbo_max = _parse_ghz(_field(raw, "Intel® Turbo Boost Max Technology 3.0 Frequency"))
    if turbo_max:
        specs["turbo_boost_max"] = "true"

    max_turbo = _max_turbo_power(raw)
    if max_turbo:
        specs["max_turbo_power"] = max_turbo

    graphics = _graphics_model(raw)
    has_igpu = graphics and "none" not in graphics.lower()
    specs["integrated_graphics"] = "true" if has_igpu else "false"
    if has_igpu:
        specs["graphics_model"] = graphics
        base = _parse_mhz(_field(raw, "Graphics Base Frequency"))
        max_clock = _graphics_max_clock(raw)
        if base:
            specs["graphics_base_clock"] = base
        if max_clock:
            specs["graphics_max_clock"] = max_clock

    specs["pcie_lanes"] = _pcie_lanes(raw, generation)
    specs["overclocking_support"] = "true" if model.endswith("K") else "false"

    popular = model in {"i9-11900K", "i7-11700K", "i5-11600K", "i9-10900K", "i7-10700K", "i5-10600K"}

    return {
        "model": model,
        "sku": entry["sku"],
        "release_date": _release_date(raw, entry.get("release_date")),
        **({"is_popular": True} if popular else {}),
        "specs": specs,
    }


def render_module(name: str, var_name: str, entries: list[dict], verified_date: str) -> str:
    lines = [
        f'"""Verified Intel Core {name} desktop CPU specifications (source: Intel ARK)."""',
        "",
        f'VERIFIED_DATE = "{verified_date}"',
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
    gen11 = sorted(
        [convert_entry(e, "11th") for e in data if "11th" in e["collection"]],
        key=lambda x: x["model"],
    )
    gen10 = sorted(
        [convert_entry(e, "10th") for e in data if "10th" in e["collection"]],
        key=lambda x: x["model"],
    )

    (OUT_DIR / "verified_intel_11th_gen.py").write_text(
        render_module("11th Gen", "INTEL_11TH_GEN_DESKTOP", gen11, "2026-09-15"),
        encoding="utf-8",
    )
    (OUT_DIR / "verified_intel_10th_gen.py").write_text(
        render_module("10th Gen", "INTEL_10TH_GEN_DESKTOP", gen10, "2026-09-15"),
        encoding="utf-8",
    )
    print(f"Wrote {len(gen11)} 11th gen and {len(gen10)} 10th gen entries")


if __name__ == "__main__":
    main()
