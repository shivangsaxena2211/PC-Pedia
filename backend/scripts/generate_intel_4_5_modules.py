"""Generate verified_intel_4th_gen.py and verified_intel_5th_gen.py from ARK fetch output."""

from __future__ import annotations

import json
import re
from pathlib import Path

ARK_DATA = Path(__file__).resolve().parent / "ark_desktop_4_5.json"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "catalog" / "cpu"
VERIFIED_DATE = "2026-09-16"

COMMON_5 = {
    "socket": "LGA 1150",
    "architecture": "Broadwell",
    "microarchitecture": "Broadwell",
    "process_node": "14 nm",
    "market_segment": "Desktop",
    "product_family": "Core",
    "generation": "5th Generation",
    "memory_channels": "2",
    "max_memory": "32",
    "memory_type": "DDR3L-1333/1600",
    "pcie_version": "3.0",
    "ecc_support": "false",
    "virtualization": "true",
    "aes": "true",
    "avx2": "true",
    "intel_turbo_boost": "true",
}

COMMON_4 = {
    "socket": "LGA 1150",
    "architecture": "Haswell",
    "microarchitecture": "Haswell",
    "process_node": "22 nm",
    "market_segment": "Desktop",
    "product_family": "Core",
    "generation": "4th Generation",
    "memory_channels": "2",
    "max_memory": "32",
    "memory_type": "DDR3-1333/1600",
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
    return fallback or "2013-06-01"


def _pcie_lanes(raw: dict) -> str:
    value = _field(raw, "Max # of PCI Express Lanes", "PCI Express Configurations")
    if value:
        match = re.search(r"^(\d+)$", value.strip())
        if match:
            return match.group(1)
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
    return value.replace("Intel® ", "Intel ").replace("®", "").replace("™", "").strip()


def _normalize_model(model: str) -> str:
    normalized = model.strip().lower()
    match = re.match(r"(i[357]-\d{4})([a-z]*)", normalized)
    if not match:
        return normalized
    return match.group(1) + match.group(2).upper()


def convert_entry(entry: dict, generation: str) -> dict:
    raw = entry.get("raw_fields", {})
    proc = _field(raw, "Processor Number")
    model = _normalize_model(proc or entry["model"])
    specs = dict(COMMON_5 if generation == "5th" else COMMON_4)

    # Prefer ARK-verified socket/process/architecture when present.
    if entry.get("specs", {}).get("socket"):
        specs["socket"] = entry["specs"]["socket"]
    if entry.get("specs", {}).get("architecture"):
        specs["architecture"] = entry["specs"]["architecture"]
        specs["microarchitecture"] = entry["specs"]["architecture"]
    if entry.get("specs", {}).get("process_node"):
        specs["process_node"] = entry["specs"]["process_node"]
    if entry.get("specs", {}).get("generation"):
        specs["generation"] = entry["specs"]["generation"]

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

    unlocked = model.endswith("K") or model.endswith("C")
    specs["overclocking_support"] = "true" if unlocked else "false"

    popular = model in {
        "i7-4770K", "i7-4790K", "i5-4690K", "i5-4670K",
        "i7-5775C", "i5-5675C",
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


def main() -> None:
    data = json.loads(ARK_DATA.read_text(encoding="utf-8"))
    gen5 = sorted(
        [convert_entry(e, "5th") for e in data if "5th" in e["collection"]],
        key=lambda x: x["model"],
    )
    gen4 = sorted(
        [convert_entry(e, "4th") for e in data if "4th" in e["collection"]],
        key=lambda x: x["model"],
    )
    (OUT_DIR / "verified_intel_5th_gen.py").write_text(
        render_module("5th Gen", "INTEL_5TH_GEN_DESKTOP", gen5),
        encoding="utf-8",
    )
    (OUT_DIR / "verified_intel_4th_gen.py").write_text(
        render_module("4th Gen", "INTEL_4TH_GEN_DESKTOP", gen4),
        encoding="utf-8",
    )
    print(f"Wrote {len(gen5)} 5th gen and {len(gen4)} 4th gen entries")


if __name__ == "__main__":
    main()
