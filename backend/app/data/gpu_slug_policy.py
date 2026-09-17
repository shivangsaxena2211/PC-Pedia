"""Canonical GPU product slug policy for PC Pedia."""

from __future__ import annotations

# Legacy seed/demo slugs mapped to canonical catalog slugs for the same GPU model.
LEGACY_GPU_SLUG_MAP: dict[str, str] = {
    "rtx-4090": "nvidia-geforce-rtx-4090",
    "rtx-4070-super": "nvidia-geforce-rtx-4070-super",
    "rx-7900-xtx": "amd-radeon-rx-7900-xtx",
    "arc-a770": "intel-arc-a770",
}


def resolve_canonical_gpu_slug(slug: str) -> str:
    return LEGACY_GPU_SLUG_MAP.get(slug, slug)
