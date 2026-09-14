"""Data provenance helpers."""

from datetime import datetime

from app import db
from app.models import DataSource, ProductSource, SpecificationSource
from app.utils.helpers import slugify


def resolve_or_create_data_source(
    name: str,
    url: str | None = None,
    description: str | None = None,
) -> DataSource:
    """Find or create a canonical DataSource record."""
    clean_name = name.strip()
    source_slug = DataSource.make_slug(clean_name)

    source = DataSource.query.filter_by(slug=source_slug).first()
    if source:
        if url and not source.url:
            source.url = url.strip()
        if description and not source.description:
            source.description = description
        return source

    if url:
        existing_by_url = DataSource.query.filter_by(url=url.strip()).first()
        if existing_by_url:
            return existing_by_url

    source = DataSource(
        name=clean_name,
        slug=source_slug,
        url=url.strip() if url else None,
        description=description,
    )
    db.session.add(source)
    db.session.flush()
    return source


def _parse_source_date(value: str | None):
    if not value:
        return None
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def upsert_product_source(
    product_id: int,
    source_data: dict | None,
) -> ProductSource | None:
    """Attach provenance metadata to a product."""
    if not source_data or not source_data.get("name"):
        return None

    source = resolve_or_create_data_source(
        name=source_data["name"],
        url=source_data.get("url"),
        description=source_data.get("notes"),
    )

    source_url = (source_data.get("url") or "").strip() or None
    source_date = _parse_source_date(source_data.get("date"))

    link = ProductSource.query.filter_by(
        product_id=product_id,
        source_id=source.id,
        source_url=source_url,
    ).first()

    if link:
        link.source_date = source_date
        link.notes = source_data.get("notes")
        return link

    link = ProductSource(
        product_id=product_id,
        source_id=source.id,
        source_url=source_url,
        source_date=source_date,
        notes=source_data.get("notes"),
    )
    db.session.add(link)
    db.session.flush()
    return link


def upsert_specification_sources(
    specification_ids: list[int],
    source_data: dict | None,
):
    """Attach the same provenance metadata to imported specifications."""
    if not source_data or not source_data.get("name"):
        return

    source = resolve_or_create_data_source(
        name=source_data["name"],
        url=source_data.get("url"),
        description=source_data.get("notes"),
    )
    source_url = (source_data.get("url") or "").strip() or None
    source_date = _parse_source_date(source_data.get("date"))

    for spec_id in specification_ids:
        existing = SpecificationSource.query.filter_by(
            specification_id=spec_id,
            source_id=source.id,
            source_url=source_url,
        ).first()
        if existing:
            existing.source_date = source_date
            existing.notes = source_data.get("notes")
            continue
        db.session.add(SpecificationSource(
            specification_id=spec_id,
            source_id=source.id,
            source_url=source_url,
            source_date=source_date,
            notes=source_data.get("notes"),
        ))
    db.session.flush()


def get_product_sources(product_id: int) -> list[dict]:
    links = (
        ProductSource.query.filter_by(product_id=product_id)
        .order_by(ProductSource.source_date.desc(), ProductSource.id.desc())
        .all()
    )
    return [link.to_dict() for link in links]
