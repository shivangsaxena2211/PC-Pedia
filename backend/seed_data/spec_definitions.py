"""Category-specific specification definitions."""

from seed_data.cpu_spec_definitions import CPU_SPECS

GPU_SPECS = [
    ("General", "Architecture", "Architecture", "string", None, True, True, False, 1),
    ("General", "Process Node", "Process Node", "string", None, True, True, False, 2),
    ("Compute", "CUDA Cores", "CUDA Cores", "integer", None, True, True, False, 10),
    ("Compute", "Stream Processors", "Stream Processors", "integer", None, True, True, False, 11),
    ("Compute", "RT Cores", "RT Cores", "integer", None, False, True, False, 12),
    ("Compute", "Tensor Cores", "Tensor Cores", "integer", None, False, True, False, 13),
    ("Memory", "VRAM", "VRAM", "string", "GB", True, True, False, 20),
    ("Memory", "Memory Type", "Memory Type", "string", None, True, True, False, 21),
    ("Memory", "Memory Bus", "Memory Bus", "string", "bit", False, True, False, 22),
    ("Memory", "Memory Bandwidth", "Memory Bandwidth", "string", "GB/s", False, True, False, 23),
    ("Clock Speeds", "Base Clock", "Base Clock", "string", "MHz", True, True, False, 30),
    ("Clock Speeds", "Boost Clock", "Boost Clock", "string", "MHz", True, True, False, 31),
    ("Power", "TDP", "TDP", "integer", "W", True, True, False, 40),
    ("Power", "TBP", "TBP", "integer", "W", False, True, False, 41),
    ("Power", "Recommended PSU", "Recommended PSU", "integer", "W", False, True, False, 42),
    ("Interface", "PCIe Interface", "PCIe Interface", "string", None, False, True, False, 50),
]

RAM_SPECS = [
    ("Memory", "DDR Generation", "DDR Generation", "string", None, True, True, True, 1),
    ("Memory", "Capacity", "Capacity", "string", "GB", True, True, True, 2),
    ("Memory", "Module Configuration", "Module Configuration", "string", None, False, True, False, 3),
    ("Performance", "Frequency", "Frequency", "integer", "MHz", True, True, False, 10),
    ("Performance", "CAS Latency", "CAS Latency", "integer", None, True, True, False, 11),
    ("Performance", "Voltage", "Voltage", "decimal", "V", False, True, False, 12),
    ("Physical", "Form Factor", "Form Factor", "string", None, True, True, False, 20),
]

SSD_SPECS = [
    ("General", "Interface", "Interface", "string", None, True, True, True, 1),
    ("General", "Form Factor", "Form Factor", "string", None, True, True, False, 2),
    ("General", "NAND Type", "NAND Type", "string", None, False, True, False, 3),
    ("Capacity", "Capacity", "Capacity", "string", "TB", True, True, True, 10),
    ("Performance", "Sequential Read", "Sequential Read", "integer", "MB/s", True, True, False, 20),
    ("Performance", "Sequential Write", "Sequential Write", "integer", "MB/s", True, True, False, 21),
    ("Endurance", "TBW", "TBW", "integer", "TB", False, True, False, 30),
    ("Endurance", "Warranty", "Warranty", "integer", "years", False, True, False, 31),
]

MOTHERBOARD_SPECS = [
    ("General", "Socket", "Socket", "string", None, True, True, True, 1),
    ("General", "Chipset", "Chipset", "string", None, True, True, False, 2),
    ("General", "Form Factor", "Form Factor", "string", None, True, True, False, 3),
    ("Memory", "RAM Type", "RAM Type", "string", None, True, True, False, 10),
    ("Memory", "Maximum RAM", "Maximum RAM", "string", "GB", False, True, False, 11),
    ("Memory", "RAM Slots", "RAM Slots", "integer", None, False, True, False, 12),
    ("Expansion", "PCIe Slots", "PCIe Slots", "string", None, False, True, False, 20),
    ("Storage", "M.2 Slots", "M.2 Slots", "integer", None, False, True, False, 30),
    ("Connectivity", "Wi-Fi", "Wi-Fi", "string", None, False, True, False, 40),
]

PSU_SPECS = [
    ("General", "Wattage", "Wattage", "integer", "W", True, True, True, 1),
    ("General", "Efficiency Rating", "Efficiency Rating", "string", None, True, True, False, 2),
    ("General", "Form Factor", "Form Factor", "string", None, True, True, False, 3),
    ("General", "Modular Type", "Modular Type", "string", None, False, True, False, 4),
    ("Connectors", "PCIe Connectors", "PCIe Connectors", "string", None, False, True, False, 10),
    ("Warranty", "Warranty", "Warranty", "integer", "years", False, True, False, 20),
]

CATEGORY_SPEC_MAP = {
    "cpu": CPU_SPECS,
    "gpu": GPU_SPECS,
    "ram": RAM_SPECS,
    "ssd": SSD_SPECS,
    "motherboards": MOTHERBOARD_SPECS,
    "psu": PSU_SPECS,
}
