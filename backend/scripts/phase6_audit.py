"""Phase 6 data quality audit."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import requests

BACKEND = Path(__file__).resolve().parents[1]
DB = BACKEND / "instance" / "pc_pedia.db"
CATALOG = BACKEND / "data" / "catalog" / "cpu"


def catalog_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(json.loads(path.read_text(encoding="utf-8")))


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    def db_gen_count(generation: str) -> int:
        return conn.execute(
            """
            SELECT COUNT(*) FROM products p
            JOIN generations g ON p.generation_id = g.id
            WHERE g.name = ?
            """,
            (generation,),
        ).fetchone()[0]

    gens = {
        "14th Gen": ("14th Generation", CATALOG / "intel/core/14th-gen/desktop.json"),
        "13th Gen": ("13th Generation", CATALOG / "intel/core/13th-gen/desktop.json"),
        "12th Gen": ("12th Generation", CATALOG / "intel/core/12th-gen/desktop.json"),
        "11th Gen": ("11th Generation", CATALOG / "intel/core/11th-gen/desktop.json"),
        "10th Gen": ("10th Generation", CATALOG / "intel/core/10th-gen/desktop.json"),
        "9th Gen": ("9th Generation", CATALOG / "intel/core/9th-gen/desktop.json"),
        "8th Gen": ("8th Generation", CATALOG / "intel/core/8th-gen/desktop.json"),
        "Ryzen 7000": ("Ryzen 7000", CATALOG / "amd/ryzen/7000/desktop.json"),
    }

    print("=== Catalog / Database Audit ===")
    total_catalog = 0
    for label, (generation, path) in gens.items():
        cat = catalog_count(path)
        db = db_gen_count(generation)
        total_catalog += cat
        print(f"{label}: catalog={cat} db={db}")

    cpu_total = conn.execute(
        """
        SELECT COUNT(*) FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE c.slug = 'cpu'
        """
    ).fetchone()[0]
    print(f"Total CPU catalog records: {total_catalog}")
    print(f"Total CPU products in DB: {cpu_total}")

    sources = conn.execute("SELECT COUNT(*) FROM data_sources").fetchone()[0]
    missing_sources = conn.execute(
        """
        SELECT COUNT(*) FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_sources ps ON ps.product_id = p.id
        WHERE c.slug = 'cpu' AND ps.id IS NULL
        """
    ).fetchone()[0]
    print(f"DataSources: {sources}, CPUs without ProductSource: {missing_sources}")

    dupes = conn.execute(
        """
        SELECT slug, COUNT(*) AS n FROM products
        GROUP BY slug HAVING n > 1
        """
    ).fetchall()
    print(f"Duplicate slugs: {len(dupes)}")

    try:
        base = "http://127.0.0.1:5000"
        for path in (
            "/api/search?q=11900K",
            "/api/search?q=10900K",
            "/api/products/cpu/intel/intel-core-i9-11900k",
            "/api/products/cpu/intel/intel-core-i9-10900k",
        ):
            r = requests.get(base + path, timeout=5)
            print(f"API {path}: {r.status_code}")
    except Exception as exc:
        print(f"API smoke test skipped: {exc}")

    conn.close()


if __name__ == "__main__":
    main()
