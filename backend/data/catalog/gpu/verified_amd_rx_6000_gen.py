"""
Verified AMD Radeon RX 6000 Series desktop GPU specifications.

Sources: official AMD Radeon RX 6000 Series product specification pages and
AMD Newsroom launch articles on amd.com.

Twelve desktop consumer models are listed on AMD's official RX 6000 Series
page. Radeon PRO, Instinct, and mobile SKUs are out of scope.
"""

VERIFIED_DATE = "2026-09-17"

SERIES_URL = "https://www.amd.com/en/products/graphics/desktops/radeon/6000-series.html"
RX_6000_LAUNCH_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2020-10-28-amd-unveils-next-generation-pc-gaming-with-amd-rad.html"
)
RX_6000_REFRESH_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2022-5-10-amd-announces-three-new-radeon-rx-6000-series-grap.html"
)
RX_6700_XT_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2021-3-3-amd-unveils-amd-radeon-rx-6700-xt-graphics-card-d.html"
)
RX_6600_XT_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2021-7-29-amd-radeon-rx-6600-xt-graphics-card-sets-new-stand.html"
)
RX_6600_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2021-10-13-amd-radeon-rx-6600-graphics-card-delivers-incredib.html"
)
RX_6500_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2022-1-4-amd-unveils-new-power-efficient-high-performance-mob.html"
)

_COMMON = {
    "architecture": "RDNA 2",
    "generation": "RX 6000 Series",
    "product_family": "Radeon RX",
    "market_segment": "desktop",
}

_RX_SERIES = "Radeon RX"
_BASE = "https://www.amd.com/en/products/graphics/desktops/radeon/6000-series/amd-radeon-rx-"

AMD_RX_6000_DESKTOP = [
    {
        "model": "RX 6950 XT",
        "series": _RX_SERIES,
        "release_date": "2022-05-10",
        "launch_msrp": "1099",
        "is_popular": True,
        "source_url": f"{_BASE}6950-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "80",
            "stream_processors": "5120",
            "ray_accelerators": "80",
            "game_clock": "2100",
            "boost_clock": "2310",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "18",
            "memory_bandwidth": "576",
            "tbp": "335",
            "recommended_psu": "850",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "2x PCIe 8-pin",
        },
    },
    {
        "model": "RX 6900 XT",
        "series": _RX_SERIES,
        "release_date": "2020-12-08",
        "launch_msrp": "999",
        "is_popular": True,
        "source_url": f"{_BASE}6900-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "80",
            "stream_processors": "5120",
            "ray_accelerators": "80",
            "game_clock": "2015",
            "boost_clock": "2250",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "16",
            "memory_bandwidth": "512",
            "tbp": "300",
            "recommended_psu": "850",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "267",
            "slot_width": "2.5-Slot",
        },
    },
    {
        "model": "RX 6800 XT",
        "series": _RX_SERIES,
        "release_date": "2020-11-18",
        "launch_msrp": "649",
        "is_popular": True,
        "source_url": f"{_BASE}6800-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "72",
            "stream_processors": "4608",
            "ray_accelerators": "72",
            "game_clock": "2015",
            "boost_clock": "2250",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "16",
            "memory_bandwidth": "512",
            "tbp": "300",
            "recommended_psu": "750",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "267",
            "slot_width": "2.5-Slot",
        },
    },
    {
        "model": "RX 6800",
        "series": _RX_SERIES,
        "release_date": "2020-11-18",
        "launch_msrp": "579",
        "is_popular": True,
        "source_url": f"{_BASE}6800.html",
        "specs": {
            **_COMMON,
            "compute_units": "60",
            "stream_processors": "3840",
            "ray_accelerators": "60",
            "game_clock": "1815",
            "boost_clock": "2105",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "16",
            "memory_bandwidth": "512",
            "tbp": "250",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "267",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RX 6750 XT",
        "series": _RX_SERIES,
        "release_date": "2022-05-10",
        "launch_msrp": "549",
        "is_popular": False,
        "source_url": f"{_BASE}6750-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "40",
            "stream_processors": "2560",
            "ray_accelerators": "40",
            "game_clock": "2495",
            "boost_clock": "2600",
            "vram_capacity": "12",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "memory_speed": "18",
            "memory_bandwidth": "432",
            "tbp": "250",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
            "length": "267",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RX 6700 XT",
        "series": _RX_SERIES,
        "release_date": "2021-03-01",
        "launch_msrp": "479",
        "is_popular": True,
        "source_url": f"{_BASE}6700-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "40",
            "stream_processors": "2560",
            "ray_accelerators": "40",
            "game_clock": "2424",
            "boost_clock": "2581",
            "vram_capacity": "12",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "memory_speed": "16",
            "memory_bandwidth": "384",
            "tbp": "230",
            "recommended_psu": "650",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
            "length": "267",
            "slot_width": "2-Slot",
        },
    },
    {
        # No official launch MSRP published on amd.com product or newsroom pages.
        "model": "RX 6700",
        "series": _RX_SERIES,
        "release_date": "2021-06-09",
        "is_popular": False,
        "source_url": f"{_BASE}6700.html",
        "specs": {
            **_COMMON,
            "compute_units": "36",
            "stream_processors": "2304",
            "ray_accelerators": "36",
            "game_clock": "2174",
            "boost_clock": "2450",
            "vram_capacity": "10",
            "vram_type": "GDDR6",
            "memory_bus_width": "160",
            "memory_speed": "16",
            "memory_bandwidth": "320",
            "tbp": "175",
            "recommended_psu": "600",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
            "length": "267",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RX 6650 XT",
        "series": _RX_SERIES,
        "release_date": "2022-05-10",
        "launch_msrp": "399",
        "is_popular": False,
        "source_url": f"{_BASE}6650-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "32",
            "stream_processors": "2048",
            "ray_accelerators": "32",
            "game_clock": "2410",
            "boost_clock": "2635",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "memory_bandwidth": "280",
            "tbp": "180",
            "recommended_psu": "500",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
        },
    },
    {
        "model": "RX 6600 XT",
        "series": _RX_SERIES,
        "release_date": "2021-08-11",
        "launch_msrp": "379",
        "is_popular": True,
        "source_url": f"{_BASE}6600-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "32",
            "stream_processors": "2048",
            "ray_accelerators": "32",
            "game_clock": "2359",
            "boost_clock": "2589",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "memory_speed": "16",
            "memory_bandwidth": "256",
            "tbp": "160",
            "recommended_psu": "500",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
        },
    },
    {
        "model": "RX 6600",
        "series": _RX_SERIES,
        "release_date": "2021-10-13",
        "launch_msrp": "329",
        "is_popular": False,
        "source_url": f"{_BASE}6600.html",
        "specs": {
            **_COMMON,
            "compute_units": "28",
            "stream_processors": "1792",
            "ray_accelerators": "28",
            "game_clock": "2044",
            "boost_clock": "2491",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "memory_speed": "14",
            "memory_bandwidth": "224",
            "tbp": "132",
            "recommended_psu": "450",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
        },
    },
    {
        "model": "RX 6500 XT",
        "series": _RX_SERIES,
        "release_date": "2022-01-19",
        "launch_msrp": "199",
        "is_popular": False,
        "source_url": f"{_BASE}6500-xt.html",
        "specs": {
            **_COMMON,
            "compute_units": "16",
            "stream_processors": "1024",
            "ray_accelerators": "16",
            "game_clock": "2650",
            "boost_clock": "2815",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "64",
            "memory_speed": "18",
            "memory_bandwidth": "144",
            "tbp": "113",
            "recommended_psu": "400",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "1x PCIe 6-pin",
            "slot_width": "2-Slot",
        },
    },
    {
        # No official standalone desktop launch MSRP on amd.com.
        "model": "RX 6400",
        "series": _RX_SERIES,
        "release_date": "2022-01-19",
        "is_popular": False,
        "source_url": f"{_BASE}6400.html",
        "specs": {
            **_COMMON,
            "compute_units": "12",
            "stream_processors": "768",
            "ray_accelerators": "12",
            "game_clock": "2039",
            "boost_clock": "2321",
            "vram_capacity": "4",
            "vram_type": "GDDR6",
            "memory_bus_width": "64",
            "memory_speed": "16",
            "memory_bandwidth": "128",
            "tbp": "53",
            "recommended_psu": "350",
            "display_outputs": "DisplayPort 1.4a, HDMI 2.1",
            "power_connectors": "PCIe Powered",
            "slot_width": "1-Slot",
        },
    },
]
