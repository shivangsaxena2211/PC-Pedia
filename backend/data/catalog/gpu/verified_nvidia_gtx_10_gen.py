"""
Verified NVIDIA GeForce GTX 10 Series desktop GPU specifications.

Sources: official NVIDIA GeForce 10 Series specification pages, product pages,
and GeForce News / Newsroom launch articles on nvidia.com.

Official specs document GTX 1060 6GB vs 3GB and GTX 1050 (2GB) / 1050 (3GB) /
1050 Ti as distinct columns — cataloged as separate products.

TITAN Xp / TITAN X (Pascal), GT 1030, Founders Edition SKUs, AIB partner cards,
laptop/Max-Q, and OEM-only configurations (e.g. GTX 1060 5GB) are out of scope.
"""

VERIFIED_DATE = "2026-09-16"

SERIES_SPECS_URL = "https://www.nvidia.com/en-gb/geforce/10-series/10-series-specs/"
SERIES_COMPARE_URL = "https://www.nvidia.com/en-sg/geforce/products/10series/compare/"
GTX_1080_TI_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/nvidia-geforce-gtx-1080-ti/"
)
GTX_1080_TI_NEWSROOM_URL = (
    "https://nvidianews.nvidia.com/news/"
    "nvidia-introduces-the-beastly-geforce-gtx-1080-ti-fastest-gaming-gpu-ever"
)
GTX_1080_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/geforce-gtx-1080-gaming-perfected/"
)
GTX_1080_NEWSROOM_URL = (
    "https://nvidianews.nvidia.com/news/"
    "a-quantum-leap-in-gaming:-nvidia-introduces-geforce-gtx-1080"
)
GTX_1070_TI_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/nvidia-geforce-gtx-1070-ti/"
)
GTX_1070_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/geforce-gtx-1070/"
)
GTX_1060_NEWS_URL = (
    "https://www.nvidia.com/en-us/geforce/news/nvidia-geforce-gtx-1060/"
)
GTX_1060_NEWSROOM_URL = (
    "https://nvidianews.nvidia.com/news/"
    "a-quantum-leap-for-every-gamer-nvidia-unveils-the-geforce-gtx-1060"
)
GTX_1060_PRODUCT_URL = (
    "https://www.nvidia.com/pt-br/geforce/products/10series/geforce-gtx-1060/"
)

_COMMON = {
    "architecture": "Pascal",
    "generation": "GTX 10 Series",
    "product_family": "GeForce",
    "market_segment": "desktop",
    "pci_express": "PCIe 3.0",
}

_GTX_SERIES = "GeForce GTX"

# Reference FE dimensions from NVIDIA 10 Series specs (inches → mm).
_H_1080 = "111"  # 4.376"
_L_1080 = "267"  # 10.5"
_H_1060 = "111"  # 4.378"
_L_1060 = "249"  # 9.823"
_H_1050 = "111"  # 4.38"
_L_1050 = "145"  # 5.7"

NVIDIA_GTX_10_DESKTOP = [
    {
        "model": "GTX 1080 Ti",
        "series": _GTX_SERIES,
        "release_date": "2017-03-10",
        "launch_msrp": "699",
        "is_popular": True,
        "source_url": GTX_1080_TI_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "3584",
            "base_clock": "1480",
            "boost_clock": "1582",
            "vram_capacity": "11",
            "vram_type": "GDDR5X",
            "memory_bus_width": "352",
            "memory_speed": "11",
            "memory_bandwidth": "484",
            "tbp": "250",
            "recommended_psu": "600",
            "display_outputs": "DP 1.4, HDMI 2.0b",
            "power_connectors": "1x PCIe 6-pin + 1x PCIe 8-pin",
            "length": _L_1080,
            "height": _H_1080,
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1080",
        "series": _GTX_SERIES,
        "release_date": "2016-05-27",
        "launch_msrp": "599",
        "is_popular": True,
        "source_url": GTX_1080_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "2560",
            "base_clock": "1607",
            "boost_clock": "1733",
            "vram_capacity": "8",
            "vram_type": "GDDR5X",
            "memory_bus_width": "256",
            "memory_speed": "10",
            "memory_bandwidth": "320",
            "tbp": "180",
            "recommended_psu": "500",
            "display_outputs": "DP 1.4, HDMI 2.0b, DL-DVI",
            "power_connectors": "1x PCIe 8-pin",
            "length": _L_1080,
            "height": _H_1080,
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1070 Ti",
        "series": _GTX_SERIES,
        "release_date": "2017-11-02",
        "launch_msrp": "449",
        "is_popular": True,
        "source_url": GTX_1070_TI_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "2432",
            "base_clock": "1607",
            "boost_clock": "1683",
            "vram_capacity": "8",
            "vram_type": "GDDR5",
            "memory_bus_width": "256",
            "memory_speed": "8",
            "memory_bandwidth": "256",
            "tbp": "180",
            "recommended_psu": "500",
            "display_outputs": "DP 1.4, HDMI 2.0b, DL-DVI",
            "power_connectors": "1x PCIe 8-pin",
            "length": _L_1080,
            "height": _H_1080,
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1070",
        "series": _GTX_SERIES,
        "release_date": "2016-06-10",
        "launch_msrp": "379",
        "is_popular": True,
        "source_url": GTX_1070_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1920",
            "base_clock": "1506",
            "boost_clock": "1683",
            "vram_capacity": "8",
            "vram_type": "GDDR5",
            "memory_bus_width": "256",
            "memory_speed": "8",
            "memory_bandwidth": "256",
            "tbp": "150",
            "recommended_psu": "500",
            "display_outputs": "DP 1.4, HDMI 2.0b, DL-DVI",
            "power_connectors": "1x PCIe 8-pin",
            "length": _L_1080,
            "height": _H_1080,
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1060 6GB",
        "series": _GTX_SERIES,
        "release_date": "2016-07-19",
        "launch_msrp": "249",
        "is_popular": True,
        "source_url": GTX_1060_NEWS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1280",
            "base_clock": "1506",
            "boost_clock": "1708",
            "vram_capacity": "6",
            "vram_type": "GDDR5",
            "memory_bus_width": "192",
            "memory_speed": "8",
            "memory_bandwidth": "192",
            "tbp": "120",
            "recommended_psu": "400",
            "display_outputs": "DP 1.4, HDMI 2.0b, Dual Link-DVI",
            "power_connectors": "1x PCIe 6-pin",
            "length": _L_1060,
            "height": _H_1060,
            "slot_width": "2-Slot",
        },
    },
    {
        # Official 10 Series specs / product page columns; no nvidia.com launch MSRP found.
        "model": "GTX 1060 3GB",
        "series": _GTX_SERIES,
        "is_popular": False,
        "source_url": SERIES_SPECS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "1152",
            "base_clock": "1506",
            "boost_clock": "1708",
            "vram_capacity": "3",
            "vram_type": "GDDR5",
            "memory_bus_width": "192",
            "memory_speed": "8",
            "memory_bandwidth": "192",
            "tbp": "120",
            "recommended_psu": "400",
            "display_outputs": "DP 1.4, HDMI 2.0b, Dual Link-DVI",
            "power_connectors": "1x PCIe 6-pin",
            "length": _L_1060,
            "height": _H_1060,
            "slot_width": "2-Slot",
        },
    },
    {
        # Official 10 Series specs columns; no nvidia.com desktop launch MSRP/date found.
        "model": "GTX 1050 Ti",
        "series": _GTX_SERIES,
        "is_popular": True,
        "source_url": SERIES_SPECS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "768",
            "base_clock": "1290",
            "boost_clock": "1392",
            "vram_capacity": "4",
            "vram_type": "GDDR5",
            "memory_bus_width": "128",
            "memory_speed": "7",
            "memory_bandwidth": "112",
            "tbp": "75",
            "recommended_psu": "300",
            "display_outputs": "DP 1.4, HDMI 2.0b, Dual Link-DVI",
            "length": _L_1050,
            "height": _H_1050,
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1050 2GB",
        "series": _GTX_SERIES,
        "is_popular": False,
        "source_url": SERIES_SPECS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "640",
            "base_clock": "1354",
            "boost_clock": "1455",
            "vram_capacity": "2",
            "vram_type": "GDDR5",
            "memory_bus_width": "128",
            "memory_speed": "7",
            "memory_bandwidth": "112",
            "tbp": "75",
            "recommended_psu": "300",
            "display_outputs": "DP 1.4, HDMI 2.0b, Dual Link-DVI",
            "length": _L_1050,
            "height": _H_1050,
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "GTX 1050 3GB",
        "series": _GTX_SERIES,
        "is_popular": False,
        "source_url": SERIES_SPECS_URL,
        "specs": {
            **_COMMON,
            "cuda_cores": "768",
            "base_clock": "1392",
            "boost_clock": "1518",
            "vram_capacity": "3",
            "vram_type": "GDDR5",
            "memory_bus_width": "96",
            "memory_speed": "7",
            "memory_bandwidth": "84",
            "tbp": "75",
            "recommended_psu": "300",
            "display_outputs": "DP 1.4, HDMI 2.0b, Dual Link-DVI",
            "length": _L_1050,
            "height": _H_1050,
            "slot_width": "2-Slot",
        },
    },
]
