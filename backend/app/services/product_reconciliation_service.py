"""Reconcile legacy seed/demo products with canonical catalog products."""

from __future__ import annotations

from dataclasses import dataclass, field

from app import db
from app.data.cpu_slug_policy import LEGACY_CPU_SLUG_MAP
from app.models import Benchmark, Product, ProductImage, ProductSource, Specification


@dataclass
class ReconciliationResult:
    merged: int = 0
    renamed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)


def _same_identity(demo: Product, canonical: Product) -> bool:
    return (
        demo.name.strip().lower() == canonical.name.strip().lower()
        and demo.manufacturer_id == canonical.manufacturer_id
        and demo.category_id == canonical.category_id
    )


def _reassign_child_rows(model, demo_id: int, canonical_id: int):
    rows = model.query.filter_by(product_id=demo_id).all()
    for row in rows:
        row.product_id = canonical_id


def _merge_product_sources(demo_id: int, canonical_id: int):
    existing = {
        (ps.source_id, ps.source_url or "")
        for ps in ProductSource.query.filter_by(product_id=canonical_id).all()
    }
    for link in ProductSource.query.filter_by(product_id=demo_id).all():
        key = (link.source_id, link.source_url or "")
        if key in existing:
            db.session.delete(link)
            continue
        link.product_id = canonical_id
        existing.add(key)


def _merge_specifications(demo: Product, canonical: Product):
    canonical_keys = {
        (spec.group_name, spec.key) for spec in canonical.specifications
    }
    for spec in demo.specifications:
        key = (spec.group_name, spec.key)
        if key in canonical_keys:
            continue
        spec.product_id = canonical.id
        canonical_keys.add(key)


def reconcile_legacy_cpu_slugs(dry_run: bool = False) -> ReconciliationResult:
    """Merge or rename legacy demo CPU slugs into canonical catalog slugs."""
    result = ReconciliationResult()

    for legacy_slug, canonical_slug in LEGACY_CPU_SLUG_MAP.items():
        demo = Product.query.filter_by(slug=legacy_slug).first()
        if not demo:
            result.skipped += 1
            continue

        canonical = Product.query.filter_by(
            category_id=demo.category_id,
            manufacturer_id=demo.manufacturer_id,
            slug=canonical_slug,
        ).first()

        if canonical and not _same_identity(demo, canonical):
            result.errors.append(
                f"Slug collision: legacy '{legacy_slug}' and canonical '{canonical_slug}' "
                f"refer to different products ({demo.name} vs {canonical.name})."
            )
            continue

        if canonical:
            action = (
                f"MERGE demo id={demo.id} ({legacy_slug}) -> canonical id={canonical.id} "
                f"({canonical_slug})"
            )
            if not dry_run:
                _reassign_child_rows(Benchmark, demo.id, canonical.id)
                _reassign_child_rows(ProductImage, demo.id, canonical.id)
                _merge_product_sources(demo.id, canonical.id)
                _merge_specifications(demo, canonical)
                if demo.is_popular and not canonical.is_popular:
                    canonical.is_popular = True
                db.session.delete(demo)
            result.merged += 1
            result.actions.append(action)
            continue

        action = f"RENAME demo id={demo.id}: {legacy_slug} -> {canonical_slug}"
        if not dry_run:
            demo.slug = canonical_slug
        result.renamed += 1
        result.actions.append(action)

    if not dry_run:
        db.session.commit()

    return result
