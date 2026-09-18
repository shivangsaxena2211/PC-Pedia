"""
Seed script for PC Hardware Database.

Usage:
    python seed.py           # Upsert seed data (preserves existing records)
    python seed.py --reset   # Drop all tables and reseed (development only)
"""
import argparse
import sys

from app import create_app, db
from app.models import (
    Category, Manufacturer, Family, Series, Generation,
    Product, Specification, SpecificationDefinition,
)
from app.services.import_service import HardwareImportService
from app.utils.helpers import slugify
from seed_data.spec_definitions import CATEGORY_SPEC_MAP


CATEGORIES = [
    ("CPU", "cpu", "Central Processing Units", "cpu", 1),
    ("GPU", "gpu", "Graphics Processing Units", "gpu", 2),
    ("RAM", "ram", "Memory Modules", "memory-stick", 3),
    ("Motherboard", "motherboards", "Motherboards", "circuit-board", 4),
    ("SSD", "ssd", "Solid State Drives", "hard-drive", 5),
    ("PSU", "psu", "Power Supply Units", "plug", 6),
    ("CPU Cooler", "coolers", "Air CPU Coolers", "fan", 7),
    ("AIO", "aio", "All-in-One Liquid Coolers", "droplets", 8),
    ("Fans", "fans", "Case Fans", "wind", 9),
    ("Cases", "cases", "PC Cases", "box", 10),
]

MANUFACTURERS = [
    "Intel", "AMD", "NVIDIA", "ASUS", "MSI", "Gigabyte", "ASRock", "Biostar",
    "Corsair", "G.Skill", "Kingston", "Crucial", "Samsung", "Western Digital",
    "Seagate", "SK hynix", "Cooler Master", "Noctua", "be quiet!", "NZXT",
    "Arctic", "Lian Li", "Thermaltake", "EVGA", "Seasonic", "Super Flower",
]

# Taxonomy: (category_slug, manufacturer, family, series, [generations])
CPU_TAXONOMY = [
    ("cpu", "Intel", "Core Ultra", "Core Ultra", ["Series 1", "Series 2"]),
    ("cpu", "Intel", "Core", "Core", [
        "14th Generation", "13th Generation", "12th Generation", "11th Generation",
        "10th Generation", "9th Generation", "8th Generation", "7th Generation",
        "6th Generation", "5th Generation", "4th Generation", "3rd Generation",
        "2nd Generation", "1st Generation",
    ]),
    ("cpu", "Intel", "Xeon", "Xeon", ["Scalable", "E", "W"]),
    ("cpu", "Intel", "Pentium", "Pentium", ["Gold", "Silver"]),
    ("cpu", "Intel", "Celeron", "Celeron", []),
    ("cpu", "Intel", "Atom", "Atom", []),
    ("cpu", "AMD", "Ryzen", "Ryzen", [
        "Ryzen 9000", "Ryzen 8000", "Ryzen 7000", "Ryzen 6000",
        "Ryzen 5000", "Ryzen 4000", "Ryzen 3000", "Ryzen 2000", "Ryzen 1000",
    ]),
    ("cpu", "AMD", "Threadripper", "Threadripper", ["7000 Series", "5000 Series", "3000 Series"]),
    ("cpu", "AMD", "EPYC", "EPYC", ["9004 Series", "7003 Series", "7002 Series"]),
    ("cpu", "AMD", "FX", "FX", []),
    ("cpu", "AMD", "Athlon", "Athlon", []),
    ("cpu", "AMD", "Phenom", "Phenom", []),
]

GPU_TAXONOMY = [
    ("gpu", "NVIDIA", "GeForce", "GeForce RTX", [
        "RTX 50 Series", "RTX 40 Series", "RTX 30 Series", "RTX 20 Series",
    ]),
    ("gpu", "NVIDIA", "GeForce GTX", "GeForce GTX", [
        "GTX 16 Series", "GTX 10 Series", "GTX 900 Series",
        "GTX 700 Series", "GTX 600 Series", "GTX 500 Series",
    ]),
    ("gpu", "AMD", "Radeon RX", "Radeon RX", [
        "RX 9000 Series", "RX 7000 Series", "RX 6000 Series", "RX 5000 Series",
        "RX 500 Series", "RX 400 Series",
    ]),
    ("gpu", "AMD", "Radeon", "Radeon", ["Vega", "R9", "R7", "R5"]),
    ("gpu", "Intel", "Arc", "Arc", ["Arc B Series", "Arc A Series", "Integrated Graphics"]),
]

OTHER_TAXONOMY = [
    ("ram", "Corsair", "Vengeance", "Vengeance LPX", ["DDR5", "DDR4", "DDR3"]),
    ("ram", "Corsair", "Vengeance", "Vengeance", ["DDR5", "DDR4", "DDR3"]),
    ("ram", "G.Skill", "Ripjaws", "Ripjaws V", ["DDR4"]),
    ("ram", "G.Skill", "Trident", "Trident Z", ["DDR5", "DDR4"]),
    ("ram", "Kingston", "Fury", "Fury Beast", ["DDR5", "DDR4"]),
    ("ram", "Crucial", "Crucial", "Crucial DDR4", ["DDR4", "DDR5"]),
    ("ssd", "Samsung", "990 Series", "990 PRO", ["NVMe", "PCIe Gen 4"]),
    ("ssd", "Western Digital", "Black", "SN850X", ["NVMe", "PCIe Gen 4"]),
    ("ssd", "Samsung", "870 EVO", "870 EVO", ["SATA", "2.5-inch"]),
    ("motherboards", "ASUS", "ROG", "ROG Strix", ["AM5", "LGA 1700", "LGA 1851"]),
    ("motherboards", "MSI", "MPG", "MPG", ["AM5", "LGA 1700"]),
    ("motherboards", "Gigabyte", "AORUS", "AORUS", ["AM5", "LGA 1700"]),
    ("psu", "Corsair", "RM Series", "RMx", ["ATX"]),
    ("psu", "Seasonic", "Focus", "Focus GX", ["ATX"]),
    ("psu", "be quiet!", "Straight Power", "Straight Power", ["ATX", "SFX"]),
    ("coolers", "Noctua", "NH-D15", "NH-D15", ["Tower Coolers"]),
    ("coolers", "Arctic", "Freezer", "Freezer", ["Tower Coolers", "Low Profile"]),
    ("aio", "NZXT", "Kraken", "Kraken", ["240mm", "280mm", "360mm"]),
    ("aio", "Corsair", "iCUE", "H150i", ["240mm", "360mm"]),
    ("fans", "Noctua", "NF-A", "NF-A", ["120mm", "140mm"]),
    ("fans", "Corsair", "LL", "LL120", ["120mm"]),
    ("cases", "Lian Li", "O11", "O11 Dynamic", ["ATX", "E-ATX"]),
    ("cases", "Fractal Design", "North", "North", ["ATX", "Mini-ITX"]),
]

# CPU demo products are imported from verified catalog JSON (data/catalog/cpu/).
# NVIDIA RTX 40 demo products are imported from verified catalog JSON
# (data/catalog/gpu/nvidia/geforce/rtx-40-series/). Seed only creates
# non-catalog demo products to avoid duplicate slug conflicts.
DEMO_PRODUCTS = [
    {
        "category": "gpu", "manufacturer": "AMD", "family": "Radeon RX", "series": "Radeon RX",
        "generation": "RX 7000 Series", "architecture": "RDNA 3",
        "product": {
            "name": "AMD Radeon RX 7900 XTX", "slug": "rx-7900-xtx",
            "release_date": "2022-12-13", "is_popular": True,
            "specifications": [
                {"group_name": "Compute", "key": "Stream Processors", "value": "6144"},
                {"group_name": "Memory", "key": "VRAM", "value": "24", "unit": "GB"},
                {"group_name": "Power", "key": "TDP", "value": "355", "unit": "W"},
            ],
        },
    },
    {
        "category": "gpu", "manufacturer": "Intel", "family": "Arc", "series": "Arc",
        "generation": "Arc A Series", "architecture": "Alchemist",
        "product": {
            "name": "Intel Arc A770", "slug": "arc-a770",
            "release_date": "2022-10-12",
            "specifications": [
                {"group_name": "General", "key": "Architecture", "value": "Alchemist"},
                {"group_name": "Memory", "key": "VRAM", "value": "16", "unit": "GB"},
            ],
        },
    },
    {
        "category": "ram", "manufacturer": "Corsair", "family": "Vengeance", "series": "Vengeance",
        "generation": "DDR5",
        "product": {
            "name": "Corsair Vengeance DDR5 32GB 6000MHz", "slug": "vengeance-ddr5-6000",
            "is_popular": True,
            "specifications": [
                {"group_name": "Memory", "key": "DDR Generation", "value": "DDR5"},
                {"group_name": "Memory", "key": "Capacity", "value": "32", "unit": "GB"},
                {"group_name": "Performance", "key": "Frequency", "value": "6000", "unit": "MHz"},
            ],
        },
    },
    {
        "category": "ram", "manufacturer": "Kingston", "family": "Fury", "series": "Fury Beast",
        "generation": "DDR4",
        "product": {
            "name": "Kingston Fury Beast DDR4 32GB 3200MHz", "slug": "fury-beast-ddr4-32gb",
            "specifications": [
                {"group_name": "Memory", "key": "DDR Generation", "value": "DDR4"},
                {"group_name": "Memory", "key": "Capacity", "value": "32", "unit": "GB"},
            ],
        },
    },
    {
        "category": "motherboards", "manufacturer": "ASUS", "family": "ROG", "series": "ROG Strix",
        "generation": "AM5",
        "product": {
            "name": "ASUS ROG Strix X670E-E Gaming WiFi", "slug": "rog-strix-x670e-e-gaming-wifi",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Socket", "value": "AM5"},
                {"group_name": "General", "key": "Chipset", "value": "AMD X670E"},
                {"group_name": "Memory", "key": "RAM Type", "value": "DDR5"},
            ],
        },
    },
    {
        "category": "ssd", "manufacturer": "Samsung", "family": "990 Series", "series": "990 PRO",
        "generation": "NVMe",
        "product": {
            "name": "Samsung 990 PRO 2TB", "slug": "990-pro-2tb",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Interface", "value": "PCIe 4.0 x4 NVMe"},
                {"group_name": "Capacity", "key": "Capacity", "value": "2", "unit": "TB"},
                {"group_name": "Performance", "key": "Sequential Read", "value": "7450", "unit": "MB/s"},
            ],
        },
    },
    {
        "category": "ssd", "manufacturer": "Samsung", "family": "870 EVO", "series": "870 EVO",
        "generation": "SATA",
        "product": {
            "name": "Samsung 870 EVO 1TB", "slug": "870-evo-1tb",
            "specifications": [
                {"group_name": "General", "key": "Interface", "value": "SATA III"},
                {"group_name": "Capacity", "key": "Capacity", "value": "1", "unit": "TB"},
            ],
        },
    },
    {
        "category": "psu", "manufacturer": "Corsair", "family": "RM Series", "series": "RMx",
        "generation": "ATX",
        "product": {
            "name": "Corsair RM1000x", "slug": "rm1000x",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Wattage", "value": "1000", "unit": "W"},
                {"group_name": "General", "key": "Efficiency Rating", "value": "80 PLUS Gold"},
            ],
        },
    },
    {
        "category": "coolers", "manufacturer": "Noctua", "family": "NH-D15", "series": "NH-D15",
        "generation": "Tower Coolers",
        "product": {
            "name": "Noctua NH-D15 chromax.black", "slug": "nh-d15-chromax-black",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Type", "value": "Dual Tower Air Cooler"},
            ],
        },
    },
    {
        "category": "aio", "manufacturer": "NZXT", "family": "Kraken", "series": "Kraken",
        "generation": "360mm",
        "product": {
            "name": "NZXT Kraken Elite 360 RGB", "slug": "kraken-elite-360-rgb",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Radiator Size", "value": "360", "unit": "mm"},
            ],
        },
    },
    {
        "category": "fans", "manufacturer": "Noctua", "family": "NF-A", "series": "NF-A",
        "generation": "120mm",
        "product": {
            "name": "Noctua NF-A12x25 PWM", "slug": "nf-a12x25-pwm",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Size", "value": "120", "unit": "mm"},
            ],
        },
    },
    {
        "category": "cases", "manufacturer": "Lian Li", "family": "O11", "series": "O11 Dynamic",
        "generation": "ATX",
        "product": {
            "name": "Lian Li O11 Dynamic EVO", "slug": "o11-dynamic-evo",
            "is_popular": True,
            "specifications": [
                {"group_name": "General", "key": "Form Factor", "value": "Mid Tower"},
            ],
        },
    },
]


def upsert_category(name, slug, description, icon, display_order):
    cat = Category.query.filter_by(slug=slug).first()
    if not cat:
        cat = Category(name=name, slug=slug, description=description, icon=icon, display_order=display_order)
        db.session.add(cat)
    else:
        cat.name = name
        cat.description = description
        cat.icon = icon
        cat.display_order = display_order
    db.session.flush()
    return cat


def upsert_manufacturer(name):
    slug = slugify(name)
    mfr = Manufacturer.query.filter_by(slug=slug).first()
    if not mfr:
        mfr = Manufacturer(name=name, slug=slug)
        db.session.add(mfr)
    db.session.flush()
    return mfr


def seed_taxonomy(taxonomy_list, order=0):
    for cat_slug, mfr_name, family_name, series_name, generations in taxonomy_list:
        cat = Category.query.filter_by(slug=cat_slug).first()
        if not cat:
            continue
        mfr = upsert_manufacturer(mfr_name)
        family_slug = slugify(family_name)
        family = Family.query.filter_by(
            category_id=cat.id, manufacturer_id=mfr.id, slug=family_slug
        ).first()
        if not family:
            family = Family(
                name=family_name, slug=family_slug,
                manufacturer_id=mfr.id, category_id=cat.id,
                display_order=order,
            )
            db.session.add(family)
            db.session.flush()

        series_slug = slugify(series_name)
        series = Series.query.filter_by(family_id=family.id, slug=series_slug).first()
        if not series:
            series = Series(
                name=series_name, slug=series_slug,
                family_id=family.id,
                manufacturer_id=mfr.id, category_id=cat.id,
                display_order=order,
            )
            db.session.add(series)
            db.session.flush()

        for i, gen_name in enumerate(generations):
            gen_slug = slugify(gen_name)
            gen = Generation.query.filter_by(series_id=series.id, slug=gen_slug).first()
            if not gen:
                gen = Generation(
                    name=gen_name, slug=gen_slug, series_id=series.id,
                    display_order=i,
                )
                db.session.add(gen)
    db.session.flush()


def seed_spec_definitions():
    for cat_slug, specs in CATEGORY_SPEC_MAP.items():
        cat = Category.query.filter_by(slug=cat_slug).first()
        if not cat:
            continue
        for group, key, display, dtype, unit, filt, comp, req, order in specs:
            existing = SpecificationDefinition.query.filter_by(
                category_id=cat.id, key=key
            ).first()
            if existing:
                existing.group_name = group
                existing.display_name = display
                existing.data_type = dtype
                existing.unit = unit
                existing.filterable = filt
                existing.comparable = comp
                existing.required = req
                existing.display_order = order
            else:
                db.session.add(SpecificationDefinition(
                    category_id=cat.id, group_name=group, key=key,
                    display_name=display, data_type=dtype, unit=unit,
                    filterable=filt, comparable=comp, required=req,
                    display_order=order,
                ))
    db.session.flush()


def migrate_legacy_series_to_families():
    """Create Family records for Series that don't have family_id set."""
    for series in Series.query.filter(Series.family_id.is_(None)).all():
        if not series.manufacturer_id or not series.category_id:
            continue
        family_slug = slugify(series.name)
        family = Family.query.filter_by(
            category_id=series.category_id,
            manufacturer_id=series.manufacturer_id,
            slug=family_slug,
        ).first()
        if not family:
            family = Family(
                name=series.name, slug=family_slug,
                manufacturer_id=series.manufacturer_id,
                category_id=series.category_id,
            )
            db.session.add(family)
            db.session.flush()
        series.family_id = family.id
    db.session.flush()


def _reset_schema():
    """Drop all tables and recreate schema via Flask-Migrate."""
    from sqlalchemy import text
    from flask_migrate import upgrade

    db.drop_all()
    with db.engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        conn.commit()
    upgrade()


def seed(reset=False):
    app = create_app()
    with app.app_context():
        if reset:
            _reset_schema()
        else:
            db.create_all()
            migrate_legacy_series_to_families()

        for name, slug, desc, icon, order in CATEGORIES:
            upsert_category(name, slug, desc, icon, order)

        for mfr_name in MANUFACTURERS:
            upsert_manufacturer(mfr_name)

        db.session.commit()

        seed_taxonomy(CPU_TAXONOMY)
        seed_taxonomy(GPU_TAXONOMY)
        seed_taxonomy(OTHER_TAXONOMY)
        seed_spec_definitions()
        db.session.commit()

        importer = HardwareImportService()
        result = importer.import_batch(DEMO_PRODUCTS)
        db.session.commit()

        print("Database seeded successfully!")
        print(f"  Categories: {Category.query.count()}")
        print(f"  Manufacturers: {Manufacturer.query.count()}")
        print(f"  Families: {Family.query.count()}")
        print(f"  Series: {Series.query.count()}")
        print(f"  Generations: {Generation.query.count()}")
        print(f"  Products: {Product.query.count()}")
        print(f"  Spec Definitions: {SpecificationDefinition.query.count()}")
        if result:
            print(f"  Import: created={result.created}, updated={result.updated}, errors={result.errors}")
            for detail in result.details:
                if detail.errors:
                    print(f"    Error: {detail.product}: {'; '.join(detail.errors)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables")
    args = parser.parse_args()
    seed(reset=args.reset)
