# CPU Catalog Data

This directory contains verified CPU import batches organized by manufacturer and family.

## Structure

```
cpu/
├── amd/
│   ├── ryzen/
│   ├── threadripper/
│   ├── epyc/
│   └── other/
└── intel/
    ├── core/
    ├── core-ultra/
    ├── xeon/
    └── other/
```

## Import

```bash
cd backend
python -m app.cli import-data data/catalog/cpu/amd/ryzen/example.json --mode=upsert
python -m app.cli import-data data/catalog/cpu/ --dry-run
```

Each JSON file should contain an array of hardware records using canonical specification keys.
