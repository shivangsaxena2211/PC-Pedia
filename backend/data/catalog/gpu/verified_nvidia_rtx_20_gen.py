"""
Verified NVIDIA GeForce RTX 20 Series desktop GPU specifications.

Sources: official NVIDIA GeForce 20 Series product specification pages, the
GeForce graphics card compare table, and GeForce News / Newsroom launch
articles on nvidia.com.

Integer RT core / tensor core counts are omitted because NVIDIA documents
generation labels (1st/2nd gen), not discrete core counts.

The official compare table lists slash-valued fields for the combined RTX 2060
column (6 GB / 12 GB). Those variants are split into separate catalog products
because NVIDIA's RTX 2060 product page documents each memory configuration in
its own specification column.
"""

VERIFIED_DATE = "2026-09-16"

SERIES_COMPARE_URL = "https://www.nvidia.com/en-us/geforce/graphics-cards/compare/"
SUPER_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/geforce-rtx-20-series-super-gpus/"
)
RTX_2060_NEWSROOM_URL = (
    "https://nvidianews.nvidia.com/news/"
    "nvidia-geforce-rtx-2060-is-here-next-gen-gaming-takes-off"
)

_COMMON = {
    "architecture": "Turing",
    "generation": "RTX 20 Series",
    "product_family": "GeForce",
    "market_segment": "desktop",
    "pci_express": "PCIe 3.0",
}

NVIDIA_RTX_20_DESKTOP = [
    {
        "model": "RTX 2080 Ti",
        "release_date": "2018-09-20",
        "launch_msrp": "999",
        "is_popular": True,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/rtx-2080-ti/",
        "specs": {
            **_COMMON,
            "cuda_cores": "4352",
            "base_clock": "1350",
            "boost_clock": "1640",
            "vram_capacity": "11",
            "vram_type": "GDDR6",
            "memory_bus_width": "352",
            "tbp": "260",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort (2), HDMI, USB Type-C",
            "maximum_displays": "4",
            "power_connectors": "2x PCIe 8-pin",
            "length": "267",
            "height": "116",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RTX 2080 SUPER",
        "release_date": "2019-07-23",
        "launch_msrp": "699",
        "is_popular": True,
        "source_url": SUPER_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "3072",
            "base_clock": "1650",
            "boost_clock": "1820",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "tbp": "250",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort (2), HDMI",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 6-pin + 1x PCIe 8-pin",
            "length": "267",
            "height": "116",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RTX 2080",
        "release_date": "2018-09-20",
        "launch_msrp": "699",
        "is_popular": True,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/rtx-2080/",
        "specs": {
            **_COMMON,
            "cuda_cores": "2944",
            "base_clock": "1520",
            "boost_clock": "1800",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "tbp": "225",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort (2), HDMI, USB Type-C",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 6-pin + 1x PCIe 8-pin",
            "length": "267",
            "height": "116",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RTX 2070 SUPER",
        "release_date": "2019-07-09",
        "launch_msrp": "499",
        "is_popular": True,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/rtx-2070-super/",
        "specs": {
            **_COMMON,
            "cuda_cores": "2560",
            "base_clock": "1605",
            "boost_clock": "1770",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "tbp": "215",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort (2), HDMI",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 6-pin + 1x PCIe 8-pin",
            "length": "267",
            "height": "116",
            "slot_width": "2-Slot",
        },
    },
    {
        # Newsroom lists October 2018 availability without a specific day.
        "model": "RTX 2070",
        "launch_msrp": "499",
        "is_popular": True,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/rtx-2070-2070-super/",
        "specs": {
            **_COMMON,
            "cuda_cores": "2304",
            "base_clock": "1410",
            "boost_clock": "1710",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "tbp": "185",
            "recommended_psu": "550",
            "display_outputs": "DisplayPort (2), HDMI, USB Type-C, DVI-DL",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 8-pin",
            "length": "229",
            "height": "113",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RTX 2060 SUPER",
        "release_date": "2019-07-09",
        "launch_msrp": "399",
        "is_popular": True,
        "source_url": SUPER_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "2176",
            "base_clock": "1470",
            "boost_clock": "1650",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "tbp": "175",
            "recommended_psu": "550",
            "display_outputs": "DisplayPort (2), HDMI, DVI-DL",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 8-pin",
            "length": "229",
            "height": "113",
            "slot_width": "2-Slot",
        },
    },
    {
        # Official RTX 2060 product page documents 12 GB in a dedicated column.
        # No official launch MSRP or launch date published on nvidia.com.
        "model": "RTX 2060 12GB",
        "is_popular": False,
        "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/rtx-2060/",
        "specs": {
            **_COMMON,
            "cuda_cores": "2176",
            "base_clock": "1470",
            "boost_clock": "1650",
            "vram_capacity": "12",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "tbp": "185",
            "recommended_psu": "550",
            "display_outputs": "DisplayPort (2), HDMI, DVI-DL",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 8-pin",
            "length": "229",
            "height": "113",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RTX 2060",
        "release_date": "2019-01-15",
        "launch_msrp": "349",
        "is_popular": True,
        "source_url": RTX_2060_NEWSROOM_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1920",
            "base_clock": "1365",
            "boost_clock": "1680",
            "vram_capacity": "6",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "tbp": "160",
            "recommended_psu": "500",
            "display_outputs": "DisplayPort (2), HDMI, USB Type-C, DVI-DL",
            "maximum_displays": "4",
            "power_connectors": "1x PCIe 8-pin",
            "length": "229",
            "height": "113",
            "slot_width": "2-Slot",
        },
    },
]
