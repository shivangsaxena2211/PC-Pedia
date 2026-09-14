# PC Pedia Hardware Data

This directory contains schemas, examples, and local import datasets for the PC Pedia hardware ingestion pipeline.

## Structure

```
data/
├── schema/          # JSON Schema and CSV column definitions
├── examples/        # Small verified example records for testing/documentation
├── imports/         # Local bulk datasets (gitignored)
└── README.md
```

## Standard JSON Format

See `schema/hardware.schema.json` for the full schema.

```json
{
  "category": "CPU",
  "manufacturer": "AMD",
  "family": "Ryzen",
  "series": "Ryzen",
  "generation": "Ryzen 7000",
  "product": {
    "name": "AMD Ryzen 7 7800X3D",
    "slug": "ryzen-7-7800x3d",
    "release_date": "2023-04-06",
    "status": "active"
  },
  "specifications": [
    { "group": "General", "key": "Socket", "value": "AM5" },
    { "group": "Core Configuration", "key": "Cores", "value": "8" }
  ],
  "images": [],
  "benchmarks": []
}
```

## CSV Format

Use `schema/hardware.csv` as the header template.

- Flat product/taxonomy columns are supported directly.
- `specifications_json` may contain a JSON array of specification objects.
- `images_json` may contain a JSON array of image objects.
- Individual `spec_<Key>` columns are also supported by the importer.

## Import CLI

From the `backend` directory:

```bash
python -m app.cli import-data data/examples/cpu.example.json --dry-run
python -m app.cli import-data data/examples/cpu.example.json --mode=upsert
python -m app.cli import-data data/examples/products.csv --mode=create
```

Modes:

- `create` — only create new products; skip existing
- `update` — create missing products and update existing products
- `upsert` — safe create-or-update (default)

## Admin API

```http
POST /api/admin/import/validate
POST /api/admin/import?mode=upsert
```

Both endpoints accept a JSON array of hardware records or a single record object.

## Rules

- Product identity is `category + manufacturer + slug`
- Generic frontend fallback SVGs must **not** be stored as `ProductImage` records
- Do not import fabricated specifications, benchmarks, or unverified image URLs
- Each product is imported atomically; one bad record does not roll back the entire batch
- Taxonomy records created for a failed product are rolled back with that product

## Local Imports

Place large local datasets in `imports/`. This folder is gitignored.
