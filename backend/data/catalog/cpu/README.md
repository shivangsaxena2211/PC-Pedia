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

## Canonical slug policy

CPU product slugs are deterministic and manufacturer-prefixed:

```text
intel-core-i9-14900k
amd-ryzen-7-7800x3d
```

Do not create alternate slugs for the same physical CPU (for example `core-i9-14900k`).
Legacy seed slugs are reconciled into canonical catalog slugs via:

```bash
python -m app.cli reconcile-cpus
```
