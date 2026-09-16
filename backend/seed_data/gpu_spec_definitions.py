"""
GPU specification definitions with canonical snake_case keys.

Manufacturer-specific compute fields (cuda_cores, stream_processors, xe_cores, etc.)
coexist without forcing equivalent values across vendors. Omit specs that do not apply.

Tuple format:
(group_name, key, display_name, data_type, unit, filterable, comparable, required, display_order)
"""

GPU_SPECS = [
    # Identity
    ("Identity", "architecture", "Architecture", "string", None, True, True, False, 1),
    ("Identity", "gpu_die", "GPU Die", "string", None, False, True, False, 2),
    ("Identity", "codename", "Codename", "string", None, False, True, False, 3),
    ("Identity", "generation", "Generation", "string", None, True, True, False, 4),
    ("Identity", "product_family", "Product Family", "string", None, False, True, False, 5),
    ("Identity", "market_segment", "Market Segment", "string", None, True, True, False, 6),
    ("Identity", "launch_msrp", "Launch MSRP", "decimal", "USD", False, True, False, 7),
    # Process
    ("Process", "process_node", "Process Node", "string", "nm", True, True, False, 10),
    # Compute — vendor-specific; only populate fields that apply
    ("Compute", "compute_units", "Compute Units", "integer", None, True, True, False, 20),
    ("Compute", "shader_units", "Shader Units", "integer", None, False, True, False, 21),
    ("Compute", "cuda_cores", "CUDA Cores", "integer", None, True, True, False, 22),
    ("Compute", "stream_processors", "Stream Processors", "integer", None, True, True, False, 23),
    ("Compute", "xe_cores", "Xe Cores", "integer", None, True, True, False, 24),
    ("Compute", "rt_cores", "RT Cores", "integer", None, False, True, False, 25),
    ("Compute", "tensor_cores", "Tensor Cores", "integer", None, False, True, False, 26),
    ("Compute", "ray_accelerators", "Ray Accelerators", "integer", None, False, True, False, 27),
    ("Compute", "xmx_engines", "XMX Engines", "integer", None, False, True, False, 28),
    ("Compute", "ray_tracing_units", "Ray Tracing Units", "integer", None, False, True, False, 29),
    # Clocks
    ("Clocks", "base_clock", "Base Clock", "decimal", "MHz", True, True, False, 30),
    ("Clocks", "boost_clock", "Boost Clock", "decimal", "MHz", True, True, False, 31),
    ("Clocks", "game_clock", "Game Clock", "decimal", "MHz", True, True, False, 32),
    ("Clocks", "memory_clock", "Memory Clock", "decimal", "MHz", False, True, False, 33),
    # Memory
    ("Memory", "vram_capacity", "VRAM Capacity", "integer", "GB", True, True, False, 40),
    ("Memory", "vram_type", "VRAM Type", "string", None, True, True, False, 41),
    ("Memory", "memory_bus_width", "Memory Bus Width", "integer", "bit", False, True, False, 42),
    ("Memory", "memory_speed", "Memory Speed", "integer", "Gbps", False, True, False, 43),
    ("Memory", "memory_bandwidth", "Memory Bandwidth", "decimal", "GB/s", True, True, False, 44),
    # Power
    ("Power", "tdp", "TDP", "integer", "W", True, True, False, 50),
    ("Power", "tbp", "TBP", "integer", "W", False, True, False, 51),
    ("Power", "board_power", "Board Power", "integer", "W", False, True, False, 52),
    ("Power", "recommended_psu", "Recommended PSU", "integer", "W", False, True, False, 53),
    # Interface
    ("Interface", "pci_express", "PCI Express", "string", None, False, True, False, 60),
    ("Interface", "display_outputs", "Display Outputs", "string", None, False, True, False, 61),
    ("Interface", "maximum_displays", "Maximum Displays", "integer", None, False, True, False, 62),
    # Physical
    ("Physical", "slot_width", "Slot Width", "string", None, False, True, False, 70),
    ("Physical", "length", "Length", "decimal", "mm", False, True, False, 71),
    ("Physical", "height", "Height", "decimal", "mm", False, True, False, 72),
    ("Physical", "power_connectors", "Power Connectors", "string", None, False, True, False, 73),
]
