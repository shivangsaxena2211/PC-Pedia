"""
Verified DDR5 desktop UDIMM RAM specifications.

Sources: official manufacturer product pages and datasheets only.
Scope: consumer desktop DDR5 UDIMM kits and modules.

Excluded from this phase:
- DDR4 / DDR3
- SO-DIMM laptop memory
- ECC / registered server memory
- Cosmetic RGB-only SKU duplicates of an otherwise identical kit
"""

VERIFIED_DATE = "2026-09-18"

_COMMON = {
    "memory_type": "DDR5",
    "form_factor": "UDIMM",
    "market_segment": "desktop",
    "generation": "DDR5",
    "ecc": "Non-ECC",
    "registered": "Unbuffered",
}

DDR5_DESKTOP_UDIMM = [
    # ── Corsair Vengeance ───────────────────────────────────────────────────
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance",
        "part_number": "CMK32GX5M2B6000C30",
        "name": "Corsair Vengeance 32GB (2 x 16GB) DDR5-6000 C30 CMK32GX5M2B6000C30",
        "is_popular": True,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk32gx5m2b6000c30/"
            "vengeance-32gb-2x16gb-ddr5-dram-6000mt-s-cl30-memory-kit-black-cmk32gx5m2b6000c30"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance",
            "part_number": "CMK32GX5M2B6000C30",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "30",
            "voltage": "1.40",
            "xmp": "XMP 3.0",
            "pin_count": "288",
        },
    },
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance",
        "part_number": "CMK32GX5M2B6000Z30",
        "name": "Corsair Vengeance 32GB (2 x 16GB) DDR5-6000 C30 EXPO CMK32GX5M2B6000Z30",
        "is_popular": True,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk32gx5m2b6000z30/"
            "vengeance-32gb-2x16gb-ddr5-dram-6000mt-s-cl30-amd-expo-memory-black-cmk32gx5m2b6000z30"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance",
            "part_number": "CMK32GX5M2B6000Z30",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "30",
            "voltage": "1.40",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
            "pin_count": "288",
        },
    },
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance",
        "part_number": "CMK64GX5M2B6000C30",
        "name": "Corsair Vengeance 64GB (2 x 32GB) DDR5-6000 C30 CMK64GX5M2B6000C30",
        "is_popular": False,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk64gx5m2b6000c30/"
            "vengeance-64gb-2x32gb-ddr5-dram-6000mt-s-cl30-memory-kit-black-cmk64gx5m2b6000c30"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance",
            "part_number": "CMK64GX5M2B6000C30",
            "module_capacity": "32",
            "total_kit_capacity": "64",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "30",
            "voltage": "1.40",
            "xmp": "XMP 3.0",
            "pin_count": "288",
        },
    },
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance",
        "part_number": "CMK16GX5M1B5600C40",
        "name": "Corsair Vengeance 16GB (1 x 16GB) DDR5-5600 C40 CMK16GX5M1B5600C40",
        "is_popular": False,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk16gx5m1b5600c40/"
            "vengeance-16gb-1x16gb-ddr5-dram-5600mt-s-cl40-memory-kit-black-cmk16gx5m1b5600c40"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance",
            "part_number": "CMK16GX5M1B5600C40",
            "module_capacity": "16",
            "total_kit_capacity": "16",
            "module_count": "1",
            "memory_speed": "5600",
            "jedec_speed": "4800",
            "cas_latency": "40",
            "voltage": "1.25",
            "xmp": "XMP 3.0",
            "pin_count": "288",
        },
    },
    # ── G.Skill Trident Z5 Neo / Aegis 5 ────────────────────────────────────
    {
        "manufacturer": "G.Skill",
        "family": "Trident",
        "series": "Trident Z5 Neo",
        "part_number": "F5-6000J3038F16GX2-TZ5N",
        "name": (
            "G.Skill Trident Z5 Neo 32GB (2 x 16GB) DDR5-6000 CL30 "
            "F5-6000J3038F16GX2-TZ5N"
        ),
        "is_popular": True,
        "source_url": (
            "https://www.gskill.com/specification/165/393/1661410171/"
            "F5-6000J3038F16GX2-TZ5N-Specification"
        ),
        "source_name": "G.Skill official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Trident Z5 Neo",
            "part_number": "F5-6000J3038F16GX2-TZ5N",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "30",
            "timings": "30-38-38-96",
            "voltage": "1.35",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
        },
    },
    {
        "manufacturer": "G.Skill",
        "family": "Trident",
        "series": "Trident Z5 Neo",
        "part_number": "F5-6000J3238F16GX2-TZ5N",
        "name": (
            "G.Skill Trident Z5 Neo 32GB (2 x 16GB) DDR5-6000 CL32 "
            "F5-6000J3238F16GX2-TZ5N"
        ),
        "is_popular": False,
        "source_url": (
            "https://www.gskill.com/specification/165/393/1662622365/"
            "F5-6000J3238F16GX2-TZ5N-Specification"
        ),
        "source_name": "G.Skill official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Trident Z5 Neo",
            "part_number": "F5-6000J3238F16GX2-TZ5N",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "32",
            "timings": "32-38-38-96",
            "voltage": "1.35",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
        },
    },
    {
        "manufacturer": "G.Skill",
        "family": "Aegis",
        "series": "Aegis 5",
        "part_number": "F5-5600J3636C16GX2-IS",
        "name": (
            "G.Skill Aegis 5 32GB (2 x 16GB) DDR5-5600 CL36 "
            "F5-5600J3636C16GX2-IS"
        ),
        "is_popular": False,
        "source_url": (
            "https://www.gskill.com/specification/165/440/1729563609/"
            "F5-5600J3636C16GX2-IS-Specification"
        ),
        "source_name": "G.Skill official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Aegis 5",
            "part_number": "F5-5600J3636C16GX2-IS",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "5600",
            "jedec_speed": "4800",
            "cas_latency": "36",
            "timings": "36-36-36-89",
            "voltage": "1.20",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
        },
    },
    # ── Kingston FURY Beast ─────────────────────────────────────────────────
    {
        "manufacturer": "Kingston",
        "family": "Fury",
        "series": "Fury Beast",
        "part_number": "KF556C40BBK2-32",
        "name": (
            "Kingston FURY Beast 32GB (2 x 16GB) DDR5-5600 CL40 "
            "KF556C40BBK2-32"
        ),
        "is_popular": True,
        "source_url": "https://www.kingston.com/datasheets/KF556C40BBK2-32.pdf",
        "source_name": "Kingston official product datasheet",
        "specs": {
            **_COMMON,
            "product_family": "FURY Beast",
            "part_number": "KF556C40BBK2-32",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "5600",
            "jedec_speed": "4800",
            "cas_latency": "40",
            "timings": "40-40-40",
            "voltage": "1.25",
            "xmp": "XMP 3.0",
            "pin_count": "288",
            "module_height": "34.9",
        },
    },
    {
        "manufacturer": "Kingston",
        "family": "Fury",
        "series": "Fury Beast",
        "part_number": "KF556C40BB2-32",
        "name": "Kingston FURY Beast 32GB (1 x 32GB) DDR5-5600 CL40 KF556C40BB2-32",
        "is_popular": False,
        "source_url": "https://www.kingston.com/datasheets/KF556C40BB2-32.pdf",
        "source_name": "Kingston official product datasheet",
        "specs": {
            **_COMMON,
            "product_family": "FURY Beast",
            "part_number": "KF556C40BB2-32",
            "module_capacity": "32",
            "total_kit_capacity": "32",
            "module_count": "1",
            "memory_speed": "5600",
            "jedec_speed": "4800",
            "cas_latency": "40",
            "timings": "40-40-40",
            "voltage": "1.25",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
            "pin_count": "288",
            "module_height": "34.9",
        },
    },
    {
        "manufacturer": "Kingston",
        "family": "Fury",
        "series": "Fury Beast",
        "part_number": "KF560C36BBEK2-32",
        "name": (
            "Kingston FURY Beast 32GB (2 x 16GB) DDR5-6000 CL36 "
            "KF560C36BBEK2-32"
        ),
        "is_popular": True,
        "source_url": "https://www.kingston.com/datasheets/KF560C36BBEK2-32.pdf",
        "source_name": "Kingston official product datasheet",
        "specs": {
            **_COMMON,
            "product_family": "FURY Beast",
            "part_number": "KF560C36BBEK2-32",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "36",
            "timings": "36-38-38",
            "voltage": "1.35",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
            "pin_count": "288",
            "module_height": "34.9",
        },
    },
    # ── Crucial ─────────────────────────────────────────────────────────────
    {
        "manufacturer": "Crucial",
        "family": "Crucial",
        "series": "Crucial DDR5",
        "part_number": "CT16G56C46U5",
        "name": "Crucial 16GB (1 x 16GB) DDR5-5600 CT16G56C46U5",
        "is_popular": False,
        "source_url": "https://www.crucial.com/memory/ddr5/ct16g56c46u5",
        "source_name": "Crucial official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Crucial DDR5",
            "part_number": "CT16G56C46U5",
            "module_capacity": "16",
            "total_kit_capacity": "16",
            "module_count": "1",
            "memory_speed": "5600",
            "jedec_speed": "5600",
            "voltage": "1.1",
        },
    },
    {
        "manufacturer": "Crucial",
        "family": "Crucial",
        "series": "Crucial Pro",
        "part_number": "CP16G56C46U5",
        "name": "Crucial Pro 16GB (1 x 16GB) DDR5-5600 CP16G56C46U5",
        "is_popular": True,
        "source_url": "https://www.crucial.com/memory/ddr5/cp16g56c46u5",
        "source_name": "Crucial official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Crucial Pro",
            "part_number": "CP16G56C46U5",
            "module_capacity": "16",
            "total_kit_capacity": "16",
            "module_count": "1",
            "memory_speed": "5600",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
        },
    },
    # ── TeamGroup Elite ─────────────────────────────────────────────────────
    {
        "manufacturer": "TeamGroup",
        "family": "Elite",
        "series": "Elite DDR5",
        "part_number": "TED532G6000C48DC01",
        "name": (
            "TeamGroup Elite 32GB (2 x 16GB) DDR5-6000 CL48 "
            "TED532G6000C48DC01"
        ),
        "is_popular": False,
        "source_url": (
            "https://www.teamgroupinc.com/en/product-detail/memory/TEAMGROUP/"
            "elite-u-dimm-ddr5/elite-u-dimm-ddr5-TED532G6000C48DC01/"
        ),
        "source_name": "TeamGroup official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Elite DDR5",
            "part_number": "TED532G6000C48DC01",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "48",
            "voltage": "1.1",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
            "module_height": "32",
        },
    },
    {
        "manufacturer": "TeamGroup",
        "family": "Elite",
        "series": "Elite DDR5",
        "part_number": "TED516G6000C4801",
        "name": "TeamGroup Elite 16GB (1 x 16GB) DDR5-6000 CL48 TED516G6000C4801",
        "is_popular": False,
        "source_url": (
            "https://www.teamgroupinc.com/en/product-detail/memory/TEAMGROUP/"
            "elite-u-dimm-ddr5/elite-u-dimm-ddr5-TED516G6000C4801/"
        ),
        "source_name": "TeamGroup official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Elite DDR5",
            "part_number": "TED516G6000C4801",
            "module_capacity": "16",
            "total_kit_capacity": "16",
            "module_count": "1",
            "memory_speed": "6000",
            "jedec_speed": "4800",
            "cas_latency": "48",
            "voltage": "1.1",
            "xmp": "XMP 3.0",
            "expo": "AMD EXPO",
            "module_height": "32",
        },
    },
]
