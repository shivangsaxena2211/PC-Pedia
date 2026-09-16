"""
Verified NVIDIA GeForce GTX 16 Series desktop GPU specifications.

Sources: official NVIDIA GeForce graphics card compare table, GTX 16 Series
product pages, and GeForce News / Newsroom launch articles on nvidia.com.

The official compare table documents GTX 1650 (G5) and GTX 1650 (G6) as
separate columns with distinct memory types and clocks. Those are cataloged as
separate products following the RTX 3050 / RTX 2060 memory-variant convention.
"""

VERIFIED_DATE = "2026-09-16"

SERIES_COMPARE_URL = "https://www.nvidia.com/en-us/geforce/graphics-cards/compare/"
SERIES_PAGE_URL = "https://www.nvidia.com/en-us/geforce/graphics-cards/16-series/"
SUPER_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/nvidia-geforce-gtx-1660-super-1650-super/"
)
GTX_1660_TI_NEWSROOM_URL = (
    "https://nvidianews.nvidia.com/news/"
    "new-geforce-gtx-1660-ti-delivers-great-performance-leap-for-every-gamer-starting-at-279"
)
GTX_1660_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/nvidia-geforce-gtx-1660/"
)
GTX_1650_NEWSROOM_URL = (
    "https://nvidianews.nvidia.com/news/"
    "nvidia-supercharges-record-80-gaming-laptop-models-with-turing-powered-gtx-16-series-gpus"
)
GTX_1630_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/f1-22-rtxon-game-ready-driver/"
)

_COMMON = {
    "architecture": "Turing",
    "generation": "GTX 16 Series",
    "product_family": "GeForce",
    "market_segment": "desktop",
    "pci_express": "PCIe 3.0",
}

_GTX_SERIES = "GeForce GTX"

NVIDIA_GTX_16_DESKTOP = [
    {
        "model": "GTX 1660 Ti",
        "series": _GTX_SERIES,
        "release_date": "2019-02-22",
        "launch_msrp": "279",
        "is_popular": True,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/gtx-1660-ti/",
        "specs": {
            **_COMMON,
            "cuda_cores": "1536",
            "base_clock": "1500",
            "boost_clock": "1770",
            "vram_capacity": "6",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "tbp": "120",
            "recommended_psu": "450",
            "display_outputs": "DP 1.4a, HDMI 2.0b, DL-DVI-D",
            "power_connectors": "1x PCIe 8-pin",
            "length": "145",
            "height": "111",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1660 SUPER",
        "series": _GTX_SERIES,
        "release_date": "2019-10-29",
        "launch_msrp": "229",
        "is_popular": True,
        "source_url": SUPER_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1408",
            "base_clock": "1530",
            "boost_clock": "1785",
            "vram_capacity": "6",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "tbp": "125",
            "recommended_psu": "450",
            "display_outputs": "DP 1.4a, HDMI 2.0b, DL-DVI-D",
            "power_connectors": "1x PCIe 8-pin",
            "length": "145",
            "height": "111",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1660",
        "series": _GTX_SERIES,
        "release_date": "2019-03-14",
        "launch_msrp": "219",
        "is_popular": True,
        "source_url": GTX_1660_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1408",
            "base_clock": "1530",
            "boost_clock": "1785",
            "vram_capacity": "6",
            "vram_type": "GDDR5",
            "memory_bus_width": "192",
            "tbp": "120",
            "recommended_psu": "450",
            "display_outputs": "DP 1.4a, HDMI 2.0b, DL-DVI-D",
            "power_connectors": "1x PCIe 8-pin",
            "length": "145",
            "height": "111",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1650 SUPER",
        "series": _GTX_SERIES,
        "release_date": "2019-11-22",
        "launch_msrp": "159",
        "is_popular": True,
        "source_url": SUPER_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1280",
            "base_clock": "1530",
            "boost_clock": "1725",
            "vram_capacity": "4",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "tbp": "100",
            "recommended_psu": "350",
            "display_outputs": "DP 1.4a, HDMI 2.0b, DL-DVI-D",
            "power_connectors": "1x PCIe 6-pin",
            "length": "160",
            "height": "115",
            "slot_width": "2-Slot",
        },
    },
    {
        # Official compare table column: GTX 1650 (G5) — original GDDR5 desktop SKU.
        "model": "GTX 1650",
        "series": _GTX_SERIES,
        "release_date": "2019-04-23",
        "launch_msrp": "149",
        "is_popular": True,
        "source_url": GTX_1650_NEWSROOM_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "896",
            "base_clock": "1485",
            "boost_clock": "1665",
            "vram_capacity": "4",
            "vram_type": "GDDR5",
            "memory_bus_width": "128",
            "tbp": "75",
            "recommended_psu": "300",
            "display_outputs": "HDMI 2.0b, DL-DVI-D",
            "power_connectors": "1x PCIe 6-pin",
            "length": "130",
            "height": "111",
            "slot_width": "2-Slot",
        },
    },
    {
        # Official compare table column: GTX 1650 (G6). No official launch date/MSRP.
        "model": "GTX 1650 GDDR6",
        "series": _GTX_SERIES,
        "is_popular": False,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/gtx-1650/",
        "specs": {
            **_COMMON,
            "cuda_cores": "896",
            "base_clock": "1410",
            "boost_clock": "1590",
            "vram_capacity": "4",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "tbp": "75",
            "recommended_psu": "300",
            "display_outputs": "HDMI 2.0b, DL-DVI-D, DP 1.4a",
            "power_connectors": "1x PCIe 6-pin",
            "length": "145",
            "height": "111",
            "slot_width": "2-Slot",
        },
    },
    {
        # No official launch MSRP published on nvidia.com.
        "model": "GTX 1630",
        "series": _GTX_SERIES,
        "release_date": "2022-06-28",
        "is_popular": False,
        "source_url": GTX_1630_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "512",
            "base_clock": "1740",
            "boost_clock": "1785",
            "vram_capacity": "4",
            "vram_type": "GDDR6",
            "memory_bus_width": "64",
            "tbp": "75",
            "recommended_psu": "300",
            "display_outputs": "HDMI 2.0b, DL-DVI-D, DP 1.4a",
            "power_connectors": "1x PCIe 6-pin",
            "length": "145",
            "height": "111",
            "slot_width": "2-Slot",
        },
    },
]
