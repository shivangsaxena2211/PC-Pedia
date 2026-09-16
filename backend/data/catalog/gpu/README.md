# GPU Catalog Data

Infrastructure for verified GPU import batches.

**Phase 2:** NVIDIA GeForce RTX 40 Series desktop catalog in `nvidia/geforce/rtx-40-series/desktop.json`.
**Phase 3:** NVIDIA GeForce RTX 30 Series desktop catalog in `nvidia/geforce/rtx-30-series/desktop.json`.

## Structure

```
gpu/
├── nvidia/
│   └── geforce/          # Desktop GeForce (initial scope)
├── amd/
│   └── radeon/           # Desktop Radeon RX / Radeon (initial scope)
└── intel/
    └── arc/              # Desktop Intel Arc (initial scope)
```

Future expansion (not yet populated):

- `nvidia/geforce-gtx/` — legacy GeForce GTX desktop
- `nvidia/quadro/`, `nvidia/tesla/` — workstation / datacenter
- `amd/radeon-pro/`, `amd/instinct/` — workstation / datacenter
- `intel/arc-pro/`, `intel/data-center-gpu/` — workstation / server
- `*/mobile/` segment batches — mobile GPU products

Market segment is expressed via the `market_segment` specification (`desktop`, `mobile`, `workstation`, `datacenter`, `server`), not only by directory path.

## Canonical slug policy

GPU product slugs are deterministic, lowercase, hyphen-separated, and manufacturer-prefixed:

```text
{manufacturer}-{family}-{model}
```

Examples:

```text
nvidia-geforce-rtx-4090
nvidia-geforce-rtx-4070-super
amd-radeon-rx-7900-xtx
intel-arc-a770
```

Rules:

1. Always start with `{manufacturer}-{family}-` (e.g. `nvidia-geforce-`, `amd-radeon-rx-`, `intel-arc-`).
2. Use only lowercase letters, digits, and hyphens.
3. Derive the model portion from the official product name without re-aliasing (no alternate slugs for the same SKU).
4. Do not omit the manufacturer or family prefix (legacy demo slugs like `rtx-4090` are not catalog slugs).

## Specification keys

Use canonical **snake_case** keys from `seed_data/gpu_spec_definitions.py`. Manufacturer-specific compute fields coexist without forcing equivalents:

| Vendor | Examples |
|--------|----------|
| NVIDIA | `cuda_cores`, `rt_cores`, `tensor_cores` |
| AMD | `stream_processors`, `compute_units`, `ray_accelerators` |
| Intel | `xe_cores`, `xmx_engines`, `ray_tracing_units` |

Omit specifications that do not apply. Do not fill absent fields with `0` or guessed values.

## Provenance

Every verified GPU catalog record **must** include a `source` block:

```json
"source": {
  "name": "NVIDIA official product specifications",
  "url": "https://www.nvidia.com/...",
  "date": "YYYY-MM-DD",
  "notes": "Optional verification notes"
}
```

Authoritative sources for the verified catalog:

| Manufacturer | Source |
|--------------|--------|
| NVIDIA | Official NVIDIA product pages (`nvidia.com`) |
| AMD | Official AMD product pages (`amd.com`) |
| Intel | Official Intel product pages (`intel.com`) |

Third-party sites are not authoritative unless explicitly approved in a later phase.

## Import

```bash
cd backend
python scripts/build_gpu_catalog.py
python scripts/build_gpu_catalog.py --validate
python scripts/build_gpu_catalog.py --dry-run
python -m app.cli import-data data/catalog/gpu/nvidia/geforce/rtx-40-series/desktop.json --dry-run
python -m app.cli import-data data/catalog/gpu/nvidia/geforce/rtx-40-series/desktop.json --mode=upsert
python -m app.cli import-data data/catalog/gpu/nvidia/geforce/rtx-30-series/desktop.json --mode=upsert
python -m app.cli reconcile-gpus
```

Legacy seed NVIDIA demo slugs (`rtx-4090`, `rtx-4070-super`) are merged into canonical catalog slugs via `reconcile-gpus`. AMD/Intel demo GPUs without a verified catalog entry are left in place until those catalogs are imported.

See `schema.json` for the record shape.
