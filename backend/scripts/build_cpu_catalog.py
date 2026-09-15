"""
Build verified CPU catalog JSON from curated Intel ARK data and AMD product pages.

Usage:
    python scripts/build_cpu_catalog.py
    python scripts/build_cpu_catalog.py --validate
    python scripts/build_cpu_catalog.py --fetch-amd
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.catalog.catalog_validation import validate_catalog_records
from data.catalog.cpu.verified_intel_8th_gen import INTEL_8TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_8
from data.catalog.cpu.verified_intel_9th_gen import INTEL_9TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_9
from data.catalog.cpu.verified_intel_10th_gen import INTEL_10TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_10
from data.catalog.cpu.verified_intel_11th_gen import INTEL_11TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_11
from data.catalog.cpu.verified_intel_12th_gen import INTEL_12TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_12
from data.catalog.cpu.verified_intel_13th_gen import INTEL_13TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_13
from data.catalog.cpu.verified_intel_14th_gen import INTEL_14TH_GEN_DESKTOP, VERIFIED_DATE as VERIFIED_DATE_14

CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "cpu"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SPEC_GROUPS = {
    "architecture": "General",
    "microarchitecture": "General",
    "process_node": "General",
    "market_segment": "General",
    "product_family": "General",
    "generation": "General",
    "socket": "Socket",
    "cores": "Core Configuration",
    "p_cores": "Core Configuration",
    "e_cores": "Core Configuration",
    "threads": "Core Configuration",
    "smt": "Core Configuration",
    "base_clock": "Clock Speeds",
    "p_core_base_clock": "Clock Speeds",
    "p_core_boost_clock": "Clock Speeds",
    "e_core_base_clock": "Clock Speeds",
    "e_core_boost_clock": "Clock Speeds",
    "boost_clock": "Clock Speeds",
    "l1_cache": "Cache",
    "l2_cache": "Cache",
    "l3_cache": "Cache",
    "v_cache": "Cache",
    "tdp": "Power",
    "processor_base_power": "Power",
    "max_turbo_power": "Power",
    "ppt": "Power",
    "package_power": "Power",
    "memory_type": "Memory",
    "memory_channels": "Memory",
    "max_memory": "Memory",
    "max_memory_speed": "Memory",
    "ecc_support": "Memory",
    "pcie_version": "PCI Express",
    "pcie_lanes": "PCI Express",
    "integrated_graphics": "Graphics",
    "graphics_model": "Graphics",
    "graphics_base_clock": "Graphics",
    "graphics_max_clock": "Graphics",
    "overclocking_support": "Features",
    "virtualization": "Features",
    "aes": "Features",
    "avx2": "Features",
    "avx512": "Features",
    "precision_boost": "Features",
    "intel_turbo_boost": "Features",
    "turbo_boost_max": "Features",
}

SPEC_UNITS = {
    "base_clock": "GHz",
    "p_core_base_clock": "GHz",
    "p_core_boost_clock": "GHz",
    "e_core_base_clock": "GHz",
    "e_core_boost_clock": "GHz",
    "boost_clock": "GHz",
    "l1_cache": "MB",
    "l2_cache": "MB",
    "l3_cache": "MB",
    "v_cache": "MB",
    "tdp": "W",
    "processor_base_power": "W",
    "max_turbo_power": "W",
    "max_memory": "GB",
    "max_memory_speed": "MT/s",
    "graphics_base_clock": "MHz",
    "graphics_max_clock": "MHz",
}

AMD_SLUGS = [
    "amd-ryzen-9-7950x3d",
    "amd-ryzen-9-7950x",
    "amd-ryzen-9-7900x3d",
    "amd-ryzen-9-7900x",
    "amd-ryzen-9-7900",
    "amd-ryzen-7-7800x3d",
    "amd-ryzen-7-7700x",
    "amd-ryzen-7-7700",
    "amd-ryzen-5-7600x3d",
    "amd-ryzen-5-7600x",
    "amd-ryzen-5-7600",
    "amd-ryzen-5-7500f",
]

AMD_REQUIRED_FIELDS = ("cores", "threads", "socket", "architecture", "base_clock", "boost_clock", "tdp")


class CatalogBuildError(Exception):
    pass


def _specs_from_dict(specs: dict) -> list[dict]:
    entries = []
    for key in sorted(specs.keys()):
        value = specs[key]
        if value is None or value == "":
            continue
        if key not in SPEC_GROUPS:
            raise CatalogBuildError(f"Unknown specification key '{key}'")
        entry = {"group": SPEC_GROUPS[key], "key": key, "value": str(value)}
        unit = SPEC_UNITS.get(key)
        if unit:
            entry["unit"] = unit
        entries.append(entry)
    return entries


def _intel_ark_url(sku: int) -> str:
    return f"https://www.intel.com/content/www/us/en/products/sku/{sku}/specifications.html"


def build_intel_record(
    entry: dict,
    *,
    generation: str,
    architecture: str,
    gen_short: str,
    verified_date: str,
) -> dict:
    model = entry["model"]
    sku = entry["sku"]
    specs = entry["specs"]
    required = ("cores", "threads", "socket", "architecture")
    missing = [field for field in required if not specs.get(field)]
    if missing:
        raise CatalogBuildError(f"Intel {model} missing required specs: {', '.join(missing)}")

    name = f"Intel Core {model}"
    slug = f"intel-core-{model.lower()}"
    has_igpu = specs.get("integrated_graphics") == "true"
    is_graphics_free = model.endswith("KF") or model.endswith("F")

    desc = (
        f"{gen_short} Intel Core desktop processor with {specs['cores']} cores "
        f"and {specs['threads']} threads."
    )
    if is_graphics_free and not has_igpu:
        desc += " Requires discrete graphics."

    record = {
        "category": "CPU",
        "manufacturer": "Intel",
        "family": "Core",
        "series": "Core",
        "generation": generation,
        "architecture": architecture,
        "source": {
            "name": "Intel ARK",
            "url": _intel_ark_url(sku),
            "date": verified_date,
            "notes": "Specifications verified against Intel ARK product specification page.",
        },
        "product": {
            "name": name,
            "slug": slug,
            "description": desc,
            "release_date": entry["release_date"],
            "status": "active",
            "is_popular": entry.get("is_popular", False),
            "architecture": architecture,
        },
        "images": [],
        "specifications": _specs_from_dict(specs),
        "benchmarks": [],
    }
    errors, _ = validate_catalog_records([record])
    if errors:
        raise CatalogBuildError(f"Intel {model} validation failed: {'; '.join(errors)}")
    return record


def build_intel_batch(
    entries: list[dict],
    *,
    generation: str,
    architecture: str,
    gen_short: str,
    verified_date: str,
) -> list[dict]:
    records = [
        build_intel_record(
            entry,
            generation=generation,
            architecture=architecture,
            gen_short=gen_short,
            verified_date=verified_date,
        )
        for entry in entries
    ]
    records.sort(key=lambda row: row["product"]["slug"])
    return records


def _amd_field(html: str, label: str) -> str | None:
    pattern = rf">\s*{re.escape(label)}.*?</dt>\s*<dd>\s*([^<]+?)\s*</dd>"
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if match:
        value = re.sub(r"\s+", " ", match.group(1)).strip()
        value = value.encode("ascii", "ignore").decode("ascii").strip()
        return value or None
    return None


def _clean_product_name(name: str) -> str:
    cleaned = name.replace("\u2122", "").replace("â¢", "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _parse_ghz(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"([\d.]+)", value.replace("Up to ", ""))
    return match.group(1) if match else None


def _parse_w(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"(\d+)", value)
    return match.group(1) if match else None


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", value.strip())
    if match:
        m, d, y = match.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return None


def build_amd_record(slug: str) -> dict:
    url = f"https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/{slug}.html"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    html = response.text

    name = _clean_product_name(_amd_field(html, "Name") or slug.replace("-", " ").title())
    cores = _amd_field(html, "# of CPU Cores")
    threads = _amd_field(html, "# of Threads")
    arch = _amd_field(html, "Processor Architecture")
    socket = _amd_field(html, "CPU Socket")
    smt = _amd_field(html, "Multithreading (SMT)")
    boost = _parse_ghz(_amd_field(html, "Max. Boost Clock"))
    base = _parse_ghz(_amd_field(html, "Base Clock"))
    l1 = _amd_field(html, "L1 Cache")
    l2 = _amd_field(html, "L2 Cache")
    l3 = _amd_field(html, "L3 Cache")
    tdp = _parse_w(_amd_field(html, "Default TDP"))
    process = _amd_field(html, "Processor Technology for CPU Cores")
    launch = _parse_date(_amd_field(html, "Launch Date"))
    memory_type = _amd_field(html, "System Memory Type")
    memory_channels = _amd_field(html, "Memory Channels")
    max_memory = _amd_field(html, "Max. Memory")
    max_mem_speed = _amd_field(html, "Max Memory Speed")
    pcie_version = _amd_field(html, "PCI Express® Version")
    pcie_lanes = _amd_field(html, "Native PCIe® Lanes (Total/Usable)")
    graphics = _amd_field(html, "Graphics Model")
    graphics_freq = _amd_field(html, "Graphics Frequency")
    unlocked = _amd_field(html, "Unlocked for Overclocking")
    ecc = _amd_field(html, "ECC Support")
    extensions = _amd_field(html, "Supported Extensions") or ""
    market = _amd_field(html, "Market Segment") or "Desktop"

    if not all([cores, threads, arch, socket, base, boost, tdp]):
        raise CatalogBuildError(f"AMD {slug}: failed to parse required fields from product page")

    specs = {
        "architecture": arch,
        "microarchitecture": arch,
        "process_node": "5" if process and "5nm" in process else None,
        "market_segment": market,
        "product_family": "Ryzen",
        "generation": "Ryzen 7000",
        "socket": socket,
        "cores": cores,
        "threads": threads,
        "smt": "true" if smt and smt.lower() == "yes" else "false",
        "base_clock": base,
        "boost_clock": boost,
        "l2_cache": re.search(r"(\d+)", l2 or "").group(1) if l2 else None,
        "l3_cache": re.search(r"(\d+)", l3 or "").group(1) if l3 else None,
        "tdp": tdp,
        "memory_type": memory_type,
        "memory_channels": memory_channels,
        "max_memory": re.search(r"(\d+)", max_memory or "").group(1) if max_memory else None,
        "max_memory_speed": (
            (m.group(1) if (m := re.search(r"DDR5-(\d+)", max_mem_speed or "")) else None)
            if max_mem_speed else None
        ),
        "ecc_support": "true" if ecc and "yes" in ecc.lower() else "false",
        "pcie_version": pcie_version.replace("PCIe® ", "PCIe ").strip() if pcie_version else None,
        "pcie_lanes": re.search(r"(\d+)", pcie_lanes or "").group(1) if pcie_lanes else None,
        "integrated_graphics": "false" if graphics and "discrete" in graphics.lower() else "true",
        "graphics_model": graphics if graphics and "discrete" not in graphics.lower() else None,
        "graphics_max_clock": re.search(r"(\d+)", graphics_freq or "").group(1) if graphics_freq else None,
        "overclocking_support": "true" if unlocked and unlocked.lower() == "yes" else "false",
        "precision_boost": "true",
        "aes": "true" if "AES" in extensions else None,
        "avx2": "true" if "AVX2" in extensions else None,
        "avx512": "true" if "AVX512" in extensions else None,
        "virtualization": "true" if "AMD-V" in extensions else None,
    }
    if l1:
        l1_kb = re.search(r"(\d+)", l1)
        if l1_kb:
            specs["l1_cache"] = (
                str(int(l1_kb.group(1)) // 1024)
                if int(l1_kb.group(1)) >= 1024
                else l1_kb.group(1)
            )

    missing = [field for field in AMD_REQUIRED_FIELDS if not specs.get(field)]
    if missing:
        raise CatalogBuildError(f"AMD {slug}: missing required specs after parse: {', '.join(missing)}")

    desc = f"Desktop processor based on the {arch} architecture with {cores} cores and {threads} threads."
    if "x3d" in slug.lower():
        desc += " Features AMD 3D V-Cache technology."

    record = {
        "category": "CPU",
        "manufacturer": "AMD",
        "family": "Ryzen",
        "series": "Ryzen",
        "generation": "Ryzen 7000",
        "architecture": arch,
        "source": {
            "name": "AMD Official Product Page",
            "url": url,
            "date": VERIFIED_DATE_14,
            "notes": "Specifications verified against AMD official product information.",
        },
        "product": {
            "name": name,
            "slug": slug,
            "description": desc,
            "release_date": launch,
            "status": "active",
            "is_popular": slug in {
                "amd-ryzen-9-7950x",
                "amd-ryzen-7-7800x3d",
                "amd-ryzen-5-7600x",
            },
            "architecture": arch,
        },
        "images": [],
        "specifications": _specs_from_dict(specs),
        "benchmarks": [],
    }
    errors, _ = validate_catalog_records([record])
    if errors:
        raise CatalogBuildError(f"AMD {slug} validation failed: {'; '.join(errors)}")
    return record


def write_catalog(path: Path, records: list[dict]):
    errors, warnings = validate_catalog_records(records)
    if errors:
        raise CatalogBuildError(f"{path}: {'; '.join(errors)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} records to {path}")


def validate_catalog_tree() -> int:
    errors_found = 0
    for path in sorted(CATALOG_ROOT.glob("**/*.json")):
        if path.read_text(encoding="utf-8").strip() in ("", "[]"):
            continue
        records = json.loads(path.read_text(encoding="utf-8"))
        errors, warnings = validate_catalog_records(records)
        if errors:
            errors_found += len(errors)
            print(f"FAIL {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"OK {path} ({len(records)} records)")
        for warning in warnings:
            print(f"  warning: {warning}")
    return 1 if errors_found else 0


def build_all(fetch_amd: bool = False):
    intel_14 = build_intel_batch(
        INTEL_14TH_GEN_DESKTOP,
        generation="14th Generation",
        architecture="Raptor Lake Refresh",
        gen_short="14th Gen",
        verified_date=VERIFIED_DATE_14,
    )
    intel_13 = build_intel_batch(
        INTEL_13TH_GEN_DESKTOP,
        generation="13th Generation",
        architecture="Raptor Lake",
        gen_short="13th Gen",
        verified_date=VERIFIED_DATE_13,
    )
    intel_12 = build_intel_batch(
        INTEL_12TH_GEN_DESKTOP,
        generation="12th Generation",
        architecture="Alder Lake",
        gen_short="12th Gen",
        verified_date=VERIFIED_DATE_12,
    )
    intel_11 = build_intel_batch(
        INTEL_11TH_GEN_DESKTOP,
        generation="11th Generation",
        architecture="Rocket Lake",
        gen_short="11th Gen",
        verified_date=VERIFIED_DATE_11,
    )
    intel_10 = build_intel_batch(
        INTEL_10TH_GEN_DESKTOP,
        generation="10th Generation",
        architecture="Comet Lake",
        gen_short="10th Gen",
        verified_date=VERIFIED_DATE_10,
    )
    intel_9 = build_intel_batch(
        INTEL_9TH_GEN_DESKTOP,
        generation="9th Generation",
        architecture="Coffee Lake Refresh",
        gen_short="9th Gen",
        verified_date=VERIFIED_DATE_9,
    )
    intel_8 = build_intel_batch(
        INTEL_8TH_GEN_DESKTOP,
        generation="8th Generation",
        architecture="Coffee Lake",
        gen_short="8th Gen",
        verified_date=VERIFIED_DATE_8,
    )

    write_catalog(CATALOG_ROOT / "intel" / "core" / "14th-gen" / "desktop.json", intel_14)
    write_catalog(CATALOG_ROOT / "intel" / "core" / "13th-gen" / "desktop.json", intel_13)
    write_catalog(CATALOG_ROOT / "intel" / "core" / "12th-gen" / "desktop.json", intel_12)
    write_catalog(CATALOG_ROOT / "intel" / "core" / "11th-gen" / "desktop.json", intel_11)
    write_catalog(CATALOG_ROOT / "intel" / "core" / "10th-gen" / "desktop.json", intel_10)
    write_catalog(CATALOG_ROOT / "intel" / "core" / "9th-gen" / "desktop.json", intel_9)
    write_catalog(CATALOG_ROOT / "intel" / "core" / "8th-gen" / "desktop.json", intel_8)

    if fetch_amd:
        amd_records = []
        for slug in AMD_SLUGS:
            print(f"Fetching AMD {slug}...")
            amd_records.append(build_amd_record(slug))
            time.sleep(0.3)
        amd_records.sort(key=lambda row: row["product"]["slug"])
        write_catalog(CATALOG_ROOT / "amd" / "ryzen" / "7000" / "desktop.json", amd_records)
    else:
        print("Skipping AMD fetch (use --fetch-amd to refresh Ryzen 7000 from AMD product pages).")


def main():
    parser = argparse.ArgumentParser(description="Build or validate verified CPU catalog JSON")
    parser.add_argument("--validate", action="store_true", help="Validate catalog JSON files only")
    parser.add_argument(
        "--fetch-amd",
        action="store_true",
        help="Fetch AMD Ryzen 7000 records from AMD product pages",
    )
    args = parser.parse_args()

    if args.validate:
        raise SystemExit(validate_catalog_tree())

    build_all(fetch_amd=args.fetch_amd)


if __name__ == "__main__":
    main()
