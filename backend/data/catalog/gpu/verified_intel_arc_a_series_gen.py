"""
Verified Intel Arc A-Series desktop GPU specifications.

Sources: official Intel ARK product specification pages, Intel Newsroom,
and Intel Gaming Access articles on intel.com.

Five desktop consumer models are listed on Intel's official Arc A-Series
desktop page. Mobile (M-suffix), embedded (E-suffix), Arc Pro, and Data
Center GPU Flex/Max products are out of scope.
"""

VERIFIED_DATE = "2026-09-17"

SERIES_URL = (
    "https://www.intel.com/content/www/us/en/products/details/"
    "discrete-gpus/arc/desktop/a-series.html"
)
A770_A750_LAUNCH_URL = (
    "https://game.intel.com/us/stories/intel-arc-graphics-a7series-perf-per-dollar/"
)
A580_LAUNCH_NEWSROOM_URL = (
    "https://newsroom.intel.com/client-computing/"
    "intel-arc-a580-graphics-available-worldwide"
)

_COMMON = {
    "architecture": "Xe HPG",
    "generation": "Arc A-Series",
    "product_family": "Arc A-Series",
    "market_segment": "desktop",
}

_ARC_SERIES = "Arc A-Series"
_BASE = "https://www.intel.com/content/www/us/en/products/sku/"

INTEL_ARC_A_SERIES_DESKTOP = [
    {
        # Intel documents 8 GB and 16 GB A770 desktop configurations; memory
        # capacity, speed, and bandwidth differ by SKU and are omitted here.
        "model": "Arc A770",
        "series": _ARC_SERIES,
        "release_date": "2022-10-12",
        "is_popular": True,
        "source_url": f"{_BASE}227955/intel-arc-a770-graphics-8gb/specifications.html",
        "specs": {
            **_COMMON,
            "xe_cores": "32",
            "ray_tracing_units": "32",
            "xmx_engines": "512",
            "boost_clock": "2100",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "tbp": "225",
            "pci_express": "PCIe 4.0 x16",
            "display_outputs": "eDP 1.4, DP 2.0 up to UHBR 10, HDMI 2.1, HDMI 2.0b",
            "maximum_displays": "4",
        },
    },
    {
        "model": "Arc A750",
        "series": _ARC_SERIES,
        "release_date": "2022-10-12",
        "launch_msrp": "289",
        "is_popular": True,
        "source_url": f"{_BASE}227954/intel-arc-a750-graphics/specifications.html",
        "specs": {
            **_COMMON,
            "xe_cores": "28",
            "ray_tracing_units": "28",
            "xmx_engines": "448",
            "boost_clock": "2050",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "16",
            "memory_bandwidth": "512",
            "tbp": "225",
            "pci_express": "PCIe 4.0 x16",
            "display_outputs": "eDP 1.4, DP 2.0 up to UHBR 10, HDMI 2.1, HDMI 2.0b",
            "maximum_displays": "4",
        },
    },
    {
        "model": "Arc A580",
        "series": _ARC_SERIES,
        "release_date": "2023-10-10",
        "launch_msrp": "179",
        "is_popular": False,
        "source_url": f"{_BASE}227961/intel-arc-a580-graphics/specifications.html",
        "specs": {
            **_COMMON,
            "xe_cores": "24",
            "ray_tracing_units": "24",
            "xmx_engines": "384",
            "boost_clock": "1700",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "16",
            "memory_bandwidth": "512",
            "tbp": "185",
            "pci_express": "PCIe 4.0 x16",
            "display_outputs": "eDP 1.4, DP 2.0 up to UHBR 10, HDMI 2.1, HDMI 2.0b",
            "maximum_displays": "4",
        },
    },
    {
        "model": "Arc A380",
        "series": _ARC_SERIES,
        "launch_msrp": "139.99",
        "is_popular": False,
        "source_url": f"{_BASE}227959/intel-arc-a380-graphics/specifications.html",
        "specs": {
            **_COMMON,
            "xe_cores": "8",
            "ray_tracing_units": "8",
            "xmx_engines": "128",
            "boost_clock": "2000",
            "vram_capacity": "6",
            "vram_type": "GDDR6",
            "memory_bus_width": "96",
            "memory_bandwidth": "186",
            "tbp": "75",
            "pci_express": "PCIe 4.0 x8 (x16 slot required)",
            "display_outputs": "eDP 1.4, DP 2.0 up to UHBR 10, HDMI 2.1, HDMI 2.0b",
            "maximum_displays": "4",
        },
    },
    {
        # Intel ARK lists launch quarter Q3'22 only; no exact launch date on intel.com.
        "model": "Arc A310",
        "series": _ARC_SERIES,
        "is_popular": False,
        "source_url": f"{_BASE}227958/intel-arc-a310-graphics/specifications.html",
        "specs": {
            **_COMMON,
            "xe_cores": "6",
            "ray_tracing_units": "6",
            "xmx_engines": "96",
            "boost_clock": "2000",
            "vram_capacity": "4",
            "vram_type": "GDDR6",
            "memory_bus_width": "64",
            "memory_bandwidth": "124",
            "tbp": "75",
            "pci_express": "PCIe 4.0 x8 (x16 slot required)",
            "display_outputs": "eDP 1.4, DP 2.0 up to UHBR 10, HDMI 2.1, HDMI 2.0b",
            "maximum_displays": "4",
        },
    },
]
