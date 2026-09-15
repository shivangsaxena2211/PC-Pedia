"""Fetch and parse Intel ARK specification pages for catalog building."""

from __future__ import annotations

import json
import re
import sys
import time
from html import unescape
from pathlib import Path

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def ark_url(sku: int) -> str:
    return f"https://www.intel.com/content/www/us/en/products/sku/{sku}/specifications.html"


def _clean(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _label_key(label: str) -> str:
    label = re.sub(r"\s*‡.*$", "", label)
    label = re.sub(r"\s*†.*$", "", label)
    label = re.sub(r"\s*For more details.*$", "", label, flags=re.IGNORECASE)
    return label.strip()


def _parse_table_fields(html: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in re.finditer(
        r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        label = _label_key(_clean(match.group(1)))
        value = _clean(match.group(2))
        value = re.sub(r"\s*‡.*$", "", value).strip()
        if label and value:
            fields[label] = value
    return fields


def _field(fields: dict[str, str], *prefixes: str) -> str | None:
    for prefix in prefixes:
        for key, value in fields.items():
            if key.startswith(prefix):
                return value
    return None


def _parse_ghz(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"([\d.]+)\s*GHz", value)
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


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    match = re.match(r"Q(\d)'(\d{2})", value.strip())
    if match:
        quarter, year_suffix = match.groups()
        year = 2000 + int(year_suffix)
        month = {"1": "01", "2": "04", "3": "07", "4": "10"}[quarter]
        return f"{year}-{month}-01"
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", value.strip())
    if match:
        m, d, y = match.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return None


def fetch_sku(sku: int) -> dict | None:
    response = requests.get(ark_url(sku), headers=HEADERS, timeout=30)
    if response.status_code != 200:
        return None
    html = response.text
    title_match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    title = title_match.group(1) if title_match else ""
    if "Intel" not in title:
        return None

    fields = _parse_table_fields(html)
    model = _field(fields, "Processor Number")
    if not model:
        model_match = re.search(r"i[3579]-\d{4}[A-Z]*", title, re.IGNORECASE)
        model = model_match.group(0).upper() if model_match else None
    if not model:
        return None
    model = model.upper()

    segment = fields.get("Vertical Segment", "")
    collection = fields.get("Product Collection", "")
    if "Desktop" not in segment and "Desktop" not in html:
        return None

    cores = _field(fields, "# of Cores", "Total Cores")
    threads = _field(fields, "# of Threads", "Total Threads")
    if not cores or not threads:
        return None

    graphics = _field(fields, "GPU Name", "Processor Graphics")
    has_igpu = bool(graphics and "none" not in graphics.lower() and "discrete" not in graphics.lower())

    launch = _parse_date(_field(fields, "Launch Date"))
    socket = _field(fields, "Sockets Supported", "Socket")
    if socket and "FCLGA" in socket:
        socket = "LGA 1200"

    code_name = _field(fields, "Code Name") or ""
    arch = "Rocket Lake" if "Rocket Lake" in code_name or "11th" in collection else None
    if not arch and ("Comet Lake" in code_name or "10th" in collection):
        arch = "Comet Lake"
    if not arch:
        if "11th" in collection:
            arch = "Rocket Lake"
        elif "10th" in collection:
            arch = "Comet Lake"

    gen = None
    if "11th" in collection:
        gen = "11th Generation"
    elif "10th" in collection:
        gen = "10th Generation"

    max_turbo = _parse_ghz(_field(fields, "Max Turbo Frequency"))
    tv_boost = _parse_ghz(_field(fields, "Intel® Thermal Velocity Boost Frequency"))
    tb3 = _parse_ghz(_field(fields, "Intel® Turbo Boost Max Technology 3.0 Frequency"))
    tb2 = _parse_ghz(_field(fields, "Intel® Turbo Boost Technology 2.0 Frequency"))
    boost_values = [v for v in [tv_boost, max_turbo, tb3, tb2] if v]
    boost = max(boost_values, key=float) if boost_values else None

    specs = {
        "socket": socket,
        "architecture": arch,
        "microarchitecture": arch,
        "process_node": "14 nm" if fields.get("Lithography") == "14 nm" else fields.get("Lithography"),
        "market_segment": segment or "Desktop",
        "product_family": "Core",
        "generation": gen,
        "cores": cores,
        "threads": threads,
        "base_clock": _parse_ghz(_field(fields, "Processor Base Frequency")),
        "boost_clock": boost,
        "l3_cache": _parse_mb(_field(fields, "Cache", "Intel® Smart Cache")),
        "tdp": _parse_w(_field(fields, "TDP")),
        "max_turbo_power": _parse_w(_field(fields, "Maximum Turbo Power")),
        "processor_base_power": _parse_w(_field(fields, "Processor Base Power")),
        "memory_type": _field(fields, "Memory Types", "Types"),
        "memory_channels": _field(fields, "Max # of Memory Channels", "# of Memory Channels"),
        "max_memory": (
            re.search(r"(\d+)", _field(fields, "Max Memory Size") or "").group(1)
            if re.search(r"(\d+)", _field(fields, "Max Memory Size") or "")
            else None
        ),
        "max_memory_speed": (
            re.search(r"-(\d+)", _field(fields, "Memory Types") or "").group(1)
            if re.search(r"-(\d+)", _field(fields, "Memory Types") or "")
            else None
        ),
        "ecc_support": "true" if (_field(fields, "ECC Memory Supported") or "").lower().startswith("yes") else "false",
        "pcie_version": (
            re.search(r"(\d+\.\d+)", _field(fields, "PCI Express Revision") or "").group(1)
            if re.search(r"(\d+\.\d+)", _field(fields, "PCI Express Revision") or "")
            else None
        ),
        "pcie_lanes": (
            re.search(r"(\d+)", _field(fields, "PCI Express Configurations") or "").group(1)
            if re.search(r"(\d+)", _field(fields, "PCI Express Configurations") or "")
            else None
        ),
        "integrated_graphics": "true" if has_igpu else "false",
        "graphics_model": graphics if has_igpu else None,
        "graphics_base_clock": (
            re.search(r"(\d+)", _field(fields, "Graphics Base Frequency") or "").group(1)
            if has_igpu and re.search(r"(\d+)", _field(fields, "Graphics Base Frequency") or "")
            else None
        ),
        "graphics_max_clock": (
            re.search(r"(\d+)", _field(fields, "Graphics Max Dynamic Frequency") or "").group(1)
            if has_igpu and re.search(r"(\d+)", _field(fields, "Graphics Max Dynamic Frequency") or "")
            else None
        ),
        "overclocking_support": "true" if model.endswith("K") else "false",
        "virtualization": "true",
        "aes": "true",
        "avx2": "true",
        "intel_turbo_boost": "true",
        "turbo_boost_max": "true" if tb3 else None,
    }

    return {
        "sku": sku,
        "model": model,
        "title": title,
        "collection": collection,
        "release_date": launch,
        "specs": {k: v for k, v in specs.items() if v},
        "raw_fields": fields,
    }


def scan_range(start: int, end: int, generation_hint: str) -> list[dict]:
    found = []
    for sku in range(start, end):
        try:
            data = fetch_sku(sku)
            if not data:
                continue
            if generation_hint not in (data.get("collection") or ""):
                continue
            found.append(data)
            print(f"FOUND {sku}: {data['model']} ({data['collection']})")
        except Exception as exc:
            print(f"ERR {sku}: {exc}")
        time.sleep(0.08)
    return found


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_intel_ark_specs.py <sku> | scan11 | scan10")
        raise SystemExit(1)

    cmd = sys.argv[1]
    if cmd == "scan11":
        results = scan_range(212300, 212450, "11th")
    elif cmd == "scan10":
        results = scan_range(199300, 199550, "10th")
    else:
        results = [fetch_sku(int(cmd))]

    out = Path(__file__).resolve().parent / "ark_scan_output.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} records to {out}")


if __name__ == "__main__":
    main()
