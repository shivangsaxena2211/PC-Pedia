# RAM Catalog Data

Verified RAM import batches organized by generation and form factor.

## Structure

```
ram/
├── ddr4/
│   └── desktop-udimm/
│       └── desktop.json
├── ddr5/
│   └── desktop-udimm/
│       └── desktop.json
├── verified_ddr4_desktop_udimm.py
├── verified_ddr5_desktop_udimm.py
└── README.md
```

Future expansion (not yet populated):

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
python -m app.cli import-data data/catalog/ram/ddr5/desktop-udimm/desktop.json --mode=upsert
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
corsair-vengeance-cmk32gx5m2b6000c30
kingston-fury-beast-kf556c40bbk2-32
gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n
```

## Specification convention

- `memory_speed` — manufacturer tested/rated data rate in **MT/s** (typically XMP/EXPO profile speed)
- `jedec_speed` — SPD/JEDEC default data rate in MT/s when documented
- `voltage` — tested/XMP/EXPO operating voltage when that is the marketed rating
- `xmp` / `expo` — profile support when officially documented
- Do not treat MT/s as physical clock frequency
- Do not treat DDR5 on-die ECC as traditional system ECC

## Provenance

Every verified RAM catalog record must include a `source` block pointing to an
official manufacturer URL (`corsair.com`, `kingston.com`, `gskill.com`,
`crucial.com`, `teamgroupinc.com`).
