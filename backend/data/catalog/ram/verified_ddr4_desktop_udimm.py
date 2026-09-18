"""
Verified DDR4 desktop UDIMM RAM specifications.

Sources: official manufacturer product pages and datasheets only.
Scope: consumer desktop DDR4 UDIMM kits and modules.

Excluded from this phase:
- DDR5 / DDR3
- SO-DIMM laptop memory
- ECC / registered server memory
- Cosmetic color variants of the same SKU
"""

VERIFIED_DATE = "2026-09-18"

_COMMON = {
    "memory_type": "DDR4",
    "form_factor": "UDIMM",
    "market_segment": "desktop",
    "generation": "DDR4",
    "ecc": "Non-ECC",
    "registered": "Unbuffered",
}

DDR4_DESKTOP_UDIMM = [
    # ── Corsair Vengeance LPX ───────────────────────────────────────────────
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance LPX",
        "part_number": "CMK8GX4M1E3200C16",
        "name": "Corsair Vengeance LPX 8GB (1 x 8GB) DDR4-3200 C16 CMK8GX4M1E3200C16",
        "is_popular": False,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk8gx4m1e3200c16/"
            "vengeance-lpx-8gb-1-x-8gb-ddr4-dram-3200mhz-c16-memory-kit-black-cmk8gx4m1e3200c16"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance LPX",
            "part_number": "CMK8GX4M1E3200C16",
            "module_capacity": "8",
            "total_kit_capacity": "8",
            "module_count": "1",
            "memory_speed": "3200",
            "jedec_speed": "2133",
            "cas_latency": "16",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
            "pin_count": "288",
        },
    },
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance LPX",
        "part_number": "CMK16GX4M2B3200C16",
        "name": "Corsair Vengeance LPX 16GB (2 x 8GB) DDR4-3200 C16 CMK16GX4M2B3200C16",
        "is_popular": True,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk16gx4m2b3200c16/"
            "vengeancea-lpx-16gb-2-x-8gb-ddr4-dram-3200mhz-c16-memory-kit-black-cmk16gx4m2b3200c16"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance LPX",
            "part_number": "CMK16GX4M2B3200C16",
            "module_capacity": "8",
            "total_kit_capacity": "16",
            "module_count": "2",
            "memory_speed": "3200",
            "jedec_speed": "2133",
            "cas_latency": "16",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
            "pin_count": "288",
        },
    },
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance LPX",
        "part_number": "CMK32GX4M2E3200C16",
        "name": "Corsair Vengeance LPX 32GB (2 x 16GB) DDR4-3200 C16 CMK32GX4M2E3200C16",
        "is_popular": True,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk32gx4m2e3200c16/"
            "vengeance-lpx-32gb-2-x-16gb-ddr4-dram-3200mhz-c16-memory-kit-black-cmk32gx4m2e3200c16"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance LPX",
            "part_number": "CMK32GX4M2E3200C16",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "3200",
            "jedec_speed": "2133",
            "cas_latency": "16",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
            "pin_count": "288",
        },
    },
    {
        "manufacturer": "Corsair",
        "family": "Vengeance",
        "series": "Vengeance LPX",
        "part_number": "CMK32GX4M2A2666C16",
        "name": "Corsair Vengeance LPX 32GB (2 x 16GB) DDR4-2666 C16 CMK32GX4M2A2666C16",
        "is_popular": False,
        "source_url": (
            "https://www.corsair.com/us/en/p/memory/cmk32gx4m2a2666c16/"
            "vengeancea-lpx-32gb-2-x-16gb-ddr4-dram-2666mhz-c16-memory-kit-black-cmk32gx4m2a2666c16"
        ),
        "source_name": "Corsair official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Vengeance LPX",
            "part_number": "CMK32GX4M2A2666C16",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "2666",
            "jedec_speed": "2133",
            "cas_latency": "16",
            "voltage": "1.2",
            "xmp": "XMP 2.0",
            "pin_count": "288",
        },
    },
    # ── Kingston FURY Beast ─────────────────────────────────────────────────
    {
        "manufacturer": "Kingston",
        "family": "Fury",
        "series": "Fury Beast",
        "part_number": "KF432C16BB/8",
        "name": "Kingston FURY Beast 8GB DDR4-3200 CL16 KF432C16BB/8",
        "is_popular": False,
        "source_url": "https://www.kingston.com/datasheets/KF432C16BB_8.pdf",
        "source_name": "Kingston official product datasheet",
        "specs": {
            **_COMMON,
            "product_family": "Fury Beast",
            "part_number": "KF432C16BB/8",
            "module_capacity": "8",
            "total_kit_capacity": "8",
            "module_count": "1",
            "memory_speed": "3200",
            "jedec_speed": "2400",
            "cas_latency": "16",
            "timings": "16-18-18",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
            "pin_count": "288",
            "module_height": "34",
        },
    },
    {
        "manufacturer": "Kingston",
        "family": "Fury",
        "series": "Fury Beast",
        "part_number": "KF432C16BB1/16",
        "name": "Kingston FURY Beast 16GB DDR4-3200 CL16 KF432C16BB1/16",
        "is_popular": False,
        "source_url": "https://www.kingston.com/dataSheets/KF432C16BB1_16.pdf",
        "source_name": "Kingston official product datasheet",
        "specs": {
            **_COMMON,
            "product_family": "Fury Beast",
            "part_number": "KF432C16BB1/16",
            "module_capacity": "16",
            "total_kit_capacity": "16",
            "module_count": "1",
            "memory_speed": "3200",
            "jedec_speed": "2400",
            "cas_latency": "16",
            "timings": "16-18-18",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
            "pin_count": "288",
            "module_height": "34",
        },
    },
    {
        "manufacturer": "Kingston",
        "family": "Fury",
        "series": "Fury Beast",
        "part_number": "KF432C16BB1K2/32",
        "name": "Kingston FURY Beast 32GB (2 x 16GB) DDR4-3200 CL16 KF432C16BB1K2/32",
        "is_popular": True,
        "source_url": "https://www.kingston.com/datasheets/KF432C16BB1K2_32.pdf",
        "source_name": "Kingston official product datasheet",
        "specs": {
            **_COMMON,
            "product_family": "Fury Beast",
            "part_number": "KF432C16BB1K2/32",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "3200",
            "jedec_speed": "2400",
            "cas_latency": "16",
            "timings": "16-18-18",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
            "pin_count": "288",
            "module_height": "34",
        },
    },
    # ── G.Skill Ripjaws V ───────────────────────────────────────────────────
    {
        "manufacturer": "G.Skill",
        "family": "Ripjaws",
        "series": "Ripjaws V",
        "part_number": "F4-3200C16D-32GVK",
        "name": "G.Skill Ripjaws V 32GB (2 x 16GB) DDR4-3200 CL16 F4-3200C16D-32GVK",
        "is_popular": True,
        "source_url": (
            "https://www.gskill.com/specification/165/184/1536110922/"
            "F4-3200C16D-32GVK-Specification"
        ),
        "source_name": "G.Skill official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Ripjaws V",
            "part_number": "F4-3200C16D-32GVK",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "3200",
            "jedec_speed": "2133",
            "cas_latency": "16",
            "timings": "16-18-18-38",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
        },
    },
    {
        "manufacturer": "G.Skill",
        "family": "Ripjaws",
        "series": "Ripjaws V",
        "part_number": "F4-3600C18D-16GVK",
        "name": "G.Skill Ripjaws V 16GB (2 x 8GB) DDR4-3600 CL18 F4-3600C18D-16GVK",
        "is_popular": False,
        "source_url": (
            "https://www.gskill.com/specification/165/184/1562832515/"
            "F4-3600C18D-16GVK-Specification"
        ),
        "source_name": "G.Skill official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Ripjaws V",
            "part_number": "F4-3600C18D-16GVK",
            "module_capacity": "8",
            "total_kit_capacity": "16",
            "module_count": "2",
            "memory_speed": "3600",
            "jedec_speed": "2133",
            "cas_latency": "18",
            "timings": "18-22-22-42",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
        },
    },
    {
        "manufacturer": "G.Skill",
        "family": "Ripjaws",
        "series": "Ripjaws V",
        "part_number": "F4-3600C18D-32GVK",
        "name": "G.Skill Ripjaws V 32GB (2 x 16GB) DDR4-3600 CL18 F4-3600C18D-32GVK",
        "is_popular": True,
        "source_url": (
            "https://www.gskill.com/specification/165/184/1562833535/"
            "F4-3600C18D-32GVK-Specification"
        ),
        "source_name": "G.Skill official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Ripjaws V",
            "part_number": "F4-3600C18D-32GVK",
            "module_capacity": "16",
            "total_kit_capacity": "32",
            "module_count": "2",
            "memory_speed": "3600",
            "jedec_speed": "2133",
            "cas_latency": "18",
            "timings": "18-22-22-42",
            "voltage": "1.35",
            "xmp": "XMP 2.0",
        },
    },
    # ── Crucial DDR4 Desktop UDIMM ──────────────────────────────────────────
    # Official product pages confirm capacity, DDR4-3200, and UDIMM form factor.
    # CAS latency / voltage were not published on the fetched Crucial pages.
    {
        "manufacturer": "Crucial",
        "family": "Crucial",
        "series": "Crucial DDR4",
        "part_number": "CT8G4DFRA32A",
        "name": "Crucial 8GB DDR4-3200 UDIMM CT8G4DFRA32A",
        "is_popular": False,
        "source_url": "https://www.crucial.com/memory/ddr4/CT8G4DFRA32A",
        "source_name": "Crucial official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Crucial DDR4",
            "part_number": "CT8G4DFRA32A",
            "module_capacity": "8",
            "total_kit_capacity": "8",
            "module_count": "1",
            "memory_speed": "3200",
        },
    },
    {
        "manufacturer": "Crucial",
        "family": "Crucial",
        "series": "Crucial DDR4",
        "part_number": "CT16G4DFRA32A",
        "name": "Crucial 16GB DDR4-3200 UDIMM CT16G4DFRA32A",
        "is_popular": False,
        "source_url": "https://www.crucial.com/memory/ddr4/CT16G4DFRA32A",
        "source_name": "Crucial official product specifications",
        "specs": {
            **_COMMON,
            "product_family": "Crucial DDR4",
            "part_number": "CT16G4DFRA32A",
            "module_capacity": "16",
            "total_kit_capacity": "16",
            "module_count": "1",
            "memory_speed": "3200",
        },
    },
]
