"""
Verified AMD Radeon RX 7000 Series desktop GPU specifications.

Sources: official AMD Radeon RX 7000 Series product specification pages and
AMD Newsroom launch articles on amd.com.

RX 7500 XT is excluded — not listed on AMD's official RX 7000 Series desktop
lineup page. Radeon PRO, Instinct, and mobile SKUs are out of scope.
"""

VERIFIED_DATE = "2026-09-17"

SERIES_URL = "https://www.amd.com/en/products/graphics/desktops/radeon/7000-series.html"
RX_7900_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2022-11-3-amd-unveils-world-s-most-advanced-gaming-graphics-.html"
)
RX_7800_7700_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2023-8-25-new-amd-radeon-rx-7800-xt-and-radeon-rx-7700-xt-gr.html"
)
RX_7600_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2023-5-24-amd-introduces-amd-radeon-rx-7600-graphics-card-f.html"
)
RX_7600_XT_NEWSROOM_URL = (
    "https://www.amd.com/en/newsroom/press-releases/"
    "2024-1-8-amd-unveils-amd-radeon-rx-7600-xt-graphics-card--.html"
)

_COMMON = {
    "architecture": "RDNA 3",
    "generation": "RX 7000 Series",
    "product_family": "Radeon RX",
    "market_segment": "desktop",
}

_RX_SERIES = "Radeon RX"

AMD_RX_7000_DESKTOP = [
    {
        "model": "RX 7900 XTX",
        "series": _RX_SERIES,
        "release_date": "2022-12-13",
        "launch_msrp": "999",
        "is_popular": True,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7900xtx.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "96",
            "stream_processors": "6144",
            "ray_accelerators": "96",
            "game_clock": "2300",
            "boost_clock": "2500",
            "vram_capacity": "24",
            "vram_type": "GDDR6",
            "memory_bus_width": "384",
            "memory_speed": "20",
            "memory_bandwidth": "960",
            "tbp": "355",
            "recommended_psu": "800",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "287",
            "slot_width": "2.5-Slot",
        },
    },
    {
        "model": "RX 7900 XT",
        "series": _RX_SERIES,
        "release_date": "2022-12-13",
        "launch_msrp": "899",
        "is_popular": True,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7900xt.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "84",
            "stream_processors": "5376",
            "ray_accelerators": "84",
            "game_clock": "2000",
            "boost_clock": "2400",
            "vram_capacity": "20",
            "vram_type": "GDDR6",
            "memory_bus_width": "320",
            "memory_speed": "20",
            "memory_bandwidth": "800",
            "tbp": "315",
            "recommended_psu": "750",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "276",
            "slot_width": "2.5-Slot",
        },
    },
    {
        # No official launch MSRP published on amd.com product or newsroom pages.
        "model": "RX 7900 GRE",
        "series": _RX_SERIES,
        "release_date": "2023-07-27",
        "is_popular": False,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7900-gre.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "80",
            "stream_processors": "5120",
            "ray_accelerators": "80",
            "game_clock": "1880",
            "boost_clock": "2245",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_speed": "18",
            "memory_bandwidth": "576",
            "tbp": "260",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
        },
    },
    {
        "model": "RX 7800 XT",
        "series": _RX_SERIES,
        "release_date": "2023-09-06",
        "launch_msrp": "499",
        "is_popular": True,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7800-xt.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "60",
            "stream_processors": "3840",
            "ray_accelerators": "60",
            "game_clock": "2124",
            "boost_clock": "2430",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "256",
            "memory_bandwidth": "624",
            "tbp": "263",
            "recommended_psu": "700",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "267",
            "slot_width": "2.5-Slot",
        },
    },
    {
        "model": "RX 7700 XT",
        "series": _RX_SERIES,
        "release_date": "2023-09-06",
        "launch_msrp": "449",
        "is_popular": True,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7700-xt.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "54",
            "stream_processors": "3456",
            "ray_accelerators": "54",
            "game_clock": "2171",
            "boost_clock": "2544",
            "vram_capacity": "12",
            "vram_type": "GDDR6",
            "memory_bus_width": "192",
            "memory_speed": "18",
            "memory_bandwidth": "432",
            "tbp": "245",
            "recommended_psu": "700",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1, USB Type-C",
            "power_connectors": "2x PCIe 8-pin",
            "length": "267",
            "slot_width": "2.5-Slot",
        },
    },
    {
        "model": "RX 7600 XT",
        "series": _RX_SERIES,
        "release_date": "2024-01-24",
        "launch_msrp": "329",
        "is_popular": False,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7600-xt.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "32",
            "stream_processors": "2048",
            "ray_accelerators": "32",
            "game_clock": "2470",
            "boost_clock": "2755",
            "vram_capacity": "16",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "memory_speed": "18",
            "memory_bandwidth": "288",
            "tbp": "190",
            "recommended_psu": "600",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1",
            "power_connectors": "2x PCIe 8-pin",
            "length": "241",
            "slot_width": "2-Slot",
        },
    },
    {
        "model": "RX 7600",
        "series": _RX_SERIES,
        "release_date": "2023-05-25",
        "launch_msrp": "269",
        "is_popular": True,
        "source_url": (
            "https://www.amd.com/en/products/graphics/desktops/radeon/"
            "7000-series/amd-radeon-rx-7600.html"
        ),
        "specs": {
            **_COMMON,
            "compute_units": "32",
            "stream_processors": "2048",
            "ray_accelerators": "32",
            "game_clock": "2250",
            "boost_clock": "2655",
            "vram_capacity": "8",
            "vram_type": "GDDR6",
            "memory_bus_width": "128",
            "memory_speed": "18",
            "memory_bandwidth": "288",
            "tbp": "165",
            "recommended_psu": "550",
            "display_outputs": "DisplayPort 2.1, HDMI 2.1",
            "power_connectors": "1x PCIe 8-pin",
            "length": "204",
            "slot_width": "2-Slot",
        },
    },
]
