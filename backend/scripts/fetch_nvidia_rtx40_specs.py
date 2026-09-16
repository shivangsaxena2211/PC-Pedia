"""Fetch and parse official NVIDIA GeForce RTX 40 Series desktop specifications."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PAGES = {
    "rtx-4090": (
        "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/",
        ["RTX 4090"],
    ),
    "rtx-4080": (
        "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4080/",
        ["RTX 4080 SUPER", "RTX 4080"],
    ),
    "rtx-4070-family": (
        "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4070-family/",
        ["RTX 4070 Ti SUPER", "RTX 4070 Ti", "RTX 4070 SUPER", "RTX 4070"],
    ),
    "rtx-4060": (
        "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4060/",
        ["RTX 4060 Ti", "RTX 4060"],
    ),
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ").replace("®", "").strip())


def parse_spec_table(html: str, models: list[str]) -> dict[str, dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    if len(tables) < 2:
        return {m: {} for m in models}
    table = tables[1]
    rows = table.find_all("tr")
    header_cells = [norm(c.get_text(" ", strip=True)) for c in rows[0].find_all(["td", "th"])]

    col_map: dict[str, int] = {}
    for idx, cell in enumerate(header_cells):
        for model in models:
            if model in cell or cell.endswith(model):
                col_map[model] = idx

    if len(models) == 1 and not col_map:
        col_map[models[0]] = len(header_cells) - 1

    specs = {m: {} for m in models}
    for row in rows[1:]:
        cells = [norm(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if not cells or all(not c for c in cells):
            continue
        if cells[0].endswith(":") and all(not cells[i] for i in range(1, len(cells))):
            continue
        if cells[0] in {
            "GPU Engine Specs:",
            "Memory Specs:",
            "Technology Support:",
            "Display Support:",
            "Card Dimensions:",
            "Thermal and Power Specs:",
        }:
            continue

        if cells[0] and cells[0] not in models and not cells[0].startswith("GeForce"):
            label = cells[0]
            values = cells[1:]
        elif len(cells) > 2 and cells[0] == "":
            label = cells[1]
            values = cells[2:]
        else:
            label = cells[0]
            values = cells[1:]

        if label in {
            "GPU Engine Specs:",
            "Memory Specs:",
            "Technology Support:",
            "Display Support:",
            "Card Dimensions:",
            "Thermal and Power Specs:",
        }:
            continue

        for model, col in col_map.items():
            vi = col - 1 if header_cells[0] == "" else col - 1
            if 0 <= vi < len(values) and values[vi]:
                specs[model][label] = values[vi]
    return specs


def parse_summary_table(html: str, models: list[str]) -> dict[str, dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")
    header = [norm(c.get_text(" ", strip=True)) for c in rows[0].find_all(["td", "th"])]
    col_map = {}
    for idx, cell in enumerate(header):
        for model in models:
            if cell == model or model in cell:
                col_map[model] = idx

    if len(models) == 1 and not col_map:
        col_map[models[0]] = len(header) - 1

    summary = {m: {} for m in models}
    for row in rows[1:]:
        cells = [norm(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        label = cells[1] if cells[0] == "" else cells[0]
        for model, col in col_map.items():
            vi = col - 1 if header[0] == "" else col
            if header[0] == "":
                vi = col - 1
            else:
                vi = col
            if vi < len(cells) and cells[vi]:
                summary[model][label] = cells[vi]
    return summary


def parse_pricing(html: str) -> list[str]:
    return re.findall(r"Starting at \$[\d,]+\.?\d*", html)


def main() -> None:
    output: dict = {}
    for key, (url, models) in PAGES.items():
        html = requests.get(url, headers=HEADERS, timeout=30).text
        output[key] = {
            "url": url,
            "models": models,
            "pricing": parse_pricing(html),
            "summary": parse_summary_table(html, models),
            "specs": parse_spec_table(html, models),
        }
    path = Path(__file__).resolve().parents[1] / "data" / "catalog" / "gpu" / "nvidia" / "geforce" / "rtx-40-series" / "_nvidia_fetched_specs.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
