# CPU Catalog Data

This directory contains verified CPU import batches organized by manufacturer and family.

## Structure

```
cpu/
├── amd/
│   ├── ryzen/
│   │   └── 7000/
│   │       └── desktop.json
│   ├── threadripper/
│   ├── epyc/
│   └── other/
└── intel/
    ├── core/
    │   └── 14th-gen/
    │       └── desktop.json
    ├── core-ultra/
    ├── xeon/
    └── other/
```

## Import

```bash
cd backend
python -m app.cli import-data data/catalog/cpu/intel/core/14th-gen/desktop.json --dry-run
python -m app.cli import-data data/catalog/cpu/amd/ryzen/7000/desktop.json --mode=upsert
python -m app.cli import-data data/catalog/cpu/ --mode=upsert
```

Rebuild catalog JSON from verified sources:

```bash
python scripts/build_cpu_catalog.py
```

Each JSON file should contain an array of hardware records using canonical specification keys.
