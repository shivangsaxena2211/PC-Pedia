"""
CPU specification definitions with canonical keys.

Tuple format:
(group_name, key, display_name, data_type, unit, filterable, comparable, required, display_order)
"""

CPU_SPECS = [
    # General
    ("General", "architecture", "Architecture", "string", None, True, True, False, 1),
    ("General", "microarchitecture", "Microarchitecture", "string", None, True, True, False, 2),
    ("General", "process_node", "Process Node", "string", "nm", True, True, False, 3),
    ("General", "market_segment", "Market Segment", "string", None, False, True, False, 4),
    ("General", "product_family", "Product Family", "string", None, False, True, False, 5),
    ("General", "generation", "Generation", "string", None, True, True, False, 6),
    # Socket
    ("Socket", "socket", "Socket", "string", None, True, True, True, 10),
    # Core Configuration
    ("Core Configuration", "cores", "Total Cores", "integer", None, True, True, False, 20),
    ("Core Configuration", "p_cores", "Performance Cores", "integer", None, True, True, False, 21),
    ("Core Configuration", "e_cores", "Efficiency Cores", "integer", None, True, True, False, 22),
    ("Core Configuration", "threads", "Threads", "integer", None, True, True, False, 23),
    ("Core Configuration", "core_complexes", "Core Complexes", "integer", None, False, True, False, 24),
    ("Core Configuration", "smt", "SMT", "boolean", None, False, True, False, 25),
    # Clock Speeds
    ("Clock Speeds", "base_clock", "Base Clock", "decimal", "GHz", True, True, False, 30),
    ("Clock Speeds", "p_core_base_clock", "Performance Core Base Clock", "decimal", "GHz", False, True, False, 31),
    ("Clock Speeds", "p_core_boost_clock", "Performance Core Boost Clock", "decimal", "GHz", True, True, False, 32),
    ("Clock Speeds", "e_core_base_clock", "Efficiency Core Base Clock", "decimal", "GHz", False, True, False, 33),
    ("Clock Speeds", "e_core_boost_clock", "Efficiency Core Boost Clock", "decimal", "GHz", False, True, False, 34),
    ("Clock Speeds", "boost_clock", "Maximum Boost Clock", "decimal", "GHz", True, True, False, 35),
    # Cache
    ("Cache", "l1_cache", "L1 Cache", "string", "MB", False, True, False, 40),
    ("Cache", "l2_cache", "L2 Cache", "string", "MB", False, True, False, 41),
    ("Cache", "l3_cache", "L3 Cache", "string", "MB", True, True, False, 42),
    ("Cache", "v_cache", "3D V-Cache", "string", "MB", True, True, False, 43),
    # Power
    ("Power", "tdp", "TDP", "integer", "W", True, True, False, 50),
    ("Power", "processor_base_power", "Processor Base Power", "integer", "W", False, True, False, 51),
    ("Power", "max_turbo_power", "Maximum Turbo Power", "integer", "W", True, True, False, 52),
    ("Power", "ppt", "PPT", "integer", "W", False, True, False, 53),
    ("Power", "package_power", "Package Power", "integer", "W", False, True, False, 54),
    # Memory
    ("Memory", "memory_type", "Memory Type", "string", None, True, True, False, 60),
    ("Memory", "memory_channels", "Memory Channels", "integer", None, False, True, False, 61),
    ("Memory", "max_memory", "Maximum Memory", "integer", "GB", False, True, False, 62),
    ("Memory", "max_memory_speed", "Maximum Memory Speed", "integer", "MT/s", False, True, False, 63),
    ("Memory", "ecc_support", "ECC Support", "boolean", None, False, True, False, 64),
    # PCI Express
    ("PCI Express", "pcie_version", "PCIe Version", "string", None, False, True, False, 70),
    ("PCI Express", "pcie_lanes", "PCIe Lanes", "integer", None, False, True, False, 71),
    # Graphics
    ("Graphics", "integrated_graphics", "Integrated Graphics", "boolean", None, False, True, False, 80),
    ("Graphics", "graphics_model", "Graphics Model", "string", None, False, True, False, 81),
    ("Graphics", "graphics_base_clock", "Graphics Base Clock", "decimal", "MHz", False, True, False, 82),
    ("Graphics", "graphics_max_clock", "Graphics Max Clock", "decimal", "MHz", False, True, False, 83),
    # Features
    ("Features", "overclocking_support", "Overclocking Support", "boolean", None, False, True, False, 90),
    ("Features", "virtualization", "Virtualization", "boolean", None, False, True, False, 91),
    ("Features", "aes", "AES", "boolean", None, False, True, False, 92),
    ("Features", "avx", "AVX", "boolean", None, False, True, False, 93),
    ("Features", "avx2", "AVX2", "boolean", None, False, True, False, 94),
    ("Features", "avx512", "AVX-512", "boolean", None, False, True, False, 95),
    ("Features", "precision_boost", "Precision Boost", "boolean", None, False, True, False, 96),
    ("Features", "intel_turbo_boost", "Intel Turbo Boost", "boolean", None, False, True, False, 97),
    ("Features", "turbo_boost_max", "Turbo Boost Max", "boolean", None, False, True, False, 98),
]
