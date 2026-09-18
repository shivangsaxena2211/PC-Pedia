"""
RAM specification definitions with canonical snake_case keys.

Tuple format:
(group_name, key, display_name, data_type, unit, filterable, comparable, required, display_order)

Convention:
- memory_speed stores the manufacturer tested/rated data rate in MT/s
  (typically the XMP/EXPO profile speed for gaming kits).
- jedec_speed stores the SPD/JEDEC default data rate in MT/s when documented.
- voltage stores the tested/XMP/EXPO operating voltage when that is the
  marketed rating; SPD/JEDEC voltage is not stored as a separate field.
- xmp / expo capture profile support when officially documented.
- Do not treat MT/s as physical clock frequency (half the effective data rate).
- Do not treat DDR5 on-die ECC as traditional system ECC (use Non-ECC for
  consumer UDIMM unless the manufacturer documents system ECC).
"""

RAM_SPECS = [
    # Identity
    ("Identity", "memory_type", "Memory Type", "string", None, True, True, True, 1),
    ("Identity", "form_factor", "Form Factor", "string", None, True, True, True, 2),
    ("Identity", "market_segment", "Market Segment", "string", None, True, True, False, 3),
    ("Identity", "product_family", "Product Family", "string", None, False, True, False, 4),
    ("Identity", "generation", "Generation", "string", None, True, True, False, 5),
    ("Identity", "part_number", "Part Number", "string", None, False, True, False, 6),
    # Capacity
    ("Capacity", "module_capacity", "Module Capacity", "integer", "GB", True, True, False, 10),
    ("Capacity", "total_kit_capacity", "Total Kit Capacity", "integer", "GB", True, True, True, 11),
    ("Capacity", "module_count", "Module Count", "integer", None, True, True, False, 12),
    # Performance
    ("Performance", "memory_speed", "Memory Speed", "integer", "MT/s", True, True, False, 20),
    ("Performance", "jedec_speed", "JEDEC Speed", "integer", "MT/s", False, True, False, 21),
    ("Performance", "cas_latency", "CAS Latency", "integer", None, True, True, False, 22),
    ("Performance", "timings", "Timings", "string", None, False, True, False, 23),
    ("Performance", "voltage", "Voltage", "decimal", "V", False, True, False, 24),
    # Features
    ("Features", "ecc", "ECC", "string", None, True, True, False, 30),
    ("Features", "registered", "Registered", "string", None, False, True, False, 31),
    ("Features", "xmp", "XMP", "string", None, True, True, False, 32),
    ("Features", "expo", "EXPO", "string", None, True, True, False, 33),
    # Physical
    ("Physical", "pin_count", "Pin Count", "integer", None, False, True, False, 40),
    ("Physical", "module_height", "Module Height", "decimal", "mm", False, True, False, 41),
]
