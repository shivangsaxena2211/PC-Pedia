# RAM Catalog Data

Verified RAM import batches organized by generation and form factor.

## Structure

```
ram/
├── ddr4/
│   └── desktop-udimm/
│       └── desktop.json
├── verified_ddr4_desktop_udimm.py
└── README.md
```

Future expansion (not yet populated):

- `ddr5/desktop-udimm/`
- `ddr4/so-dimm/`
- `ddr3/`
- ECC / registered server memory

## Import

```bash
cd backend
python scripts/build_ram_catalog.py
python scripts/build_ram_catalog.py --validate
python scripts/build_ram_catalog.py --dry-run
python -m app.cli import-data data/catalog/ram/ddr4/desktop-udimm/desktop.json --mode=upsert
python -m app.cli reconcile-rams
```

## Canonical slug policy

RAM product slugs are deterministic and include the manufacturer part number:

```text
{manufacturer}-{series}-{part-number}
```

Examples:

```text
corsair-vengeance-lpx-cmk16gx4m2b3200c16
kingston-fury-beast-kf432c16bb1k2-32
gskill-ripjaws-v-f4-3200c16d-32gvk
```

## Specification convention

- `memory_speed` — manufacturer tested/rated data rate in **MT/s** (typically XMP profile speed)
- `jedec_speed` — SPD/JEDEC default data rate in MT/s when documented
- Do not treat MT/s as physical clock frequency

## Provenance

Every verified RAM catalog record must include a `source` block pointing to an
official manufacturer URL (`corsair.com`, `kingston.com`, `gskill.com`, `crucial.com`).
