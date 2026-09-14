"""
Reusable hardware import service for future JSON/CSV data ingestion.

Usage:
    from app.services.import_service import HardwareImportService
    service = HardwareImportService()
    result = service.import_record(record_dict)
    results = service.import_batch(records_list)
"""

from datetime import datetime

from app import db
from app.models import (
    Category, Manufacturer, Family, Series, Generation,
    Product, Specification, SpecificationDefinition,
)
from app.utils.helpers import slugify
from app.utils.validation import ValidationError, validate_specifications


class ImportResult:
    def __init__(self):
        self.created = []
        self.updated = []
        self.skipped = []
        self.errors = []

    def to_dict(self):
        return {
            "created": len(self.created),
            "updated": len(self.updated),
            "skipped": len(self.skipped),
            "errors": self.errors,
            "created_ids": self.created,
            "updated_ids": self.updated,
        }


class HardwareImportService:
    """Import structured hardware records into the taxonomy + product tables."""

    def resolve_category(self, slug_or_name: str) -> Category | None:
        slug = slugify(slug_or_name)
        cat = Category.query.filter(
            db.or_(Category.slug == slug, Category.name.ilike(slug_or_name))
        ).first()
        return cat

    def resolve_or_create_manufacturer(self, name: str, **extra) -> Manufacturer:
        slug = extra.get("slug") or slugify(name)
        mfr = Manufacturer.query.filter_by(slug=slug).first()
        if mfr:
            return mfr
        mfr = Manufacturer(name=name, slug=slug, **{k: v for k, v in extra.items() if k != "slug"})
        db.session.add(mfr)
        db.session.flush()
        return mfr

    def resolve_or_create_family(
        self, name: str, manufacturer: Manufacturer, category: Category, **extra
    ) -> Family:
        slug = extra.get("slug") or slugify(name)
        family = Family.query.filter_by(
            category_id=category.id,
            manufacturer_id=manufacturer.id,
            slug=slug,
        ).first()
        if family:
            return family
        family = Family(
            name=name,
            slug=slug,
            manufacturer_id=manufacturer.id,
            category_id=category.id,
            description=extra.get("description"),
            display_order=extra.get("display_order", 0),
        )
        db.session.add(family)
        db.session.flush()
        return family

    def resolve_or_create_series(
        self, name: str, family: Family, **extra
    ) -> Series:
        slug = extra.get("slug") or slugify(name)
        series = Series.query.filter_by(family_id=family.id, slug=slug).first()
        if series:
            return series
        series = Series(
            name=name,
            slug=slug,
            family_id=family.id,
            manufacturer_id=family.manufacturer_id,
            category_id=family.category_id,
            description=extra.get("description"),
            display_order=extra.get("display_order", 0),
        )
        db.session.add(series)
        db.session.flush()
        return series

    def resolve_or_create_generation(
        self, name: str, series: Series, **extra
    ) -> Generation | None:
        if not name:
            return None
        slug = extra.get("slug") or slugify(name)
        gen = Generation.query.filter_by(series_id=series.id, slug=slug).first()
        if gen:
            return gen
        release_date = extra.get("release_date")
        if release_date and isinstance(release_date, str):
            release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
        gen = Generation(
            name=name,
            slug=slug,
            series_id=series.id,
            architecture=extra.get("architecture"),
            release_year=extra.get("release_year"),
            release_date=release_date,
            description=extra.get("description"),
            display_order=extra.get("display_order", 0),
        )
        db.session.add(gen)
        db.session.flush()
        return gen

    def import_record(self, record: dict) -> tuple[Product | None, str]:
        """
        Import a single hardware record.

        Expected record structure:
        {
            "category": "cpu",
            "manufacturer": "AMD",
            "family": "Ryzen",
            "series": "Ryzen 7000",
            "generation": "Zen 4",  # optional
            "product": {
                "name": "AMD Ryzen 7 7800X3D",
                "slug": "ryzen-7-7800x3d",
                "architecture": "Zen 4",
                "release_date": "2023-04-06",
                "description": "...",
                "specifications": [{"group_name": "...", "key": "...", "value": "..."}]
            }
        }
        """
        try:
            category = self.resolve_category(record["category"])
            if not category:
                return None, f"Category not found: {record['category']}"

            manufacturer = self.resolve_or_create_manufacturer(record["manufacturer"])
            family = self.resolve_or_create_family(
                record.get("family") or record.get("series", "General"),
                manufacturer,
                category,
            )
            series = self.resolve_or_create_series(
                record.get("series") or record.get("family", "General"),
                family,
            )
            generation = None
            if record.get("generation"):
                generation = self.resolve_or_create_generation(
                    record["generation"],
                    series,
                    architecture=record.get("architecture"),
                )

            product_data = record["product"]
            slug = product_data.get("slug") or slugify(product_data["name"])

            existing = Product.query.filter_by(
                category_id=category.id,
                manufacturer_id=manufacturer.id,
                slug=slug,
            ).first()

            specs = product_data.get("specifications", [])
            if specs:
                validate_specifications(category.id, specs)

            release_date = product_data.get("release_date")
            if release_date and isinstance(release_date, str):
                release_date = datetime.strptime(release_date, "%Y-%m-%d").date()

            if existing:
                existing.name = product_data["name"]
                existing.family_id = family.id
                existing.series_id = series.id
                existing.generation_id = generation.id if generation else None
                existing.architecture = product_data.get("architecture")
                existing.description = product_data.get("description")
                existing.release_date = release_date
                existing.image_url = product_data.get("image_url")
                existing.status = product_data.get("status", "active")
                self._update_specs(existing, specs)
                return existing, "updated"

            product = Product(
                name=product_data["name"],
                slug=slug,
                category_id=category.id,
                manufacturer_id=manufacturer.id,
                family_id=family.id,
                series_id=series.id,
                generation_id=generation.id if generation else None,
                architecture=product_data.get("architecture"),
                description=product_data.get("description"),
                release_date=release_date,
                image_url=product_data.get("image_url"),
                status=product_data.get("status", "active"),
                is_popular=product_data.get("is_popular", False),
            )
            db.session.add(product)
            db.session.flush()
            self._update_specs(product, specs)
            return product, "created"

        except ValidationError as e:
            return None, e.message
        except Exception as e:
            return None, str(e)

    def _update_specs(self, product: Product, specs: list[dict]):
        Specification.query.filter_by(product_id=product.id).delete()
        for i, spec in enumerate(specs):
            db.session.add(
                Specification(
                    product_id=product.id,
                    group_name=spec.get("group_name") or spec.get("group", "General"),
                    key=spec["key"],
                    value=str(spec["value"]),
                    unit=spec.get("unit"),
                    sort_order=spec.get("sort_order", i),
                )
            )

    def import_batch(self, records: list[dict], commit: bool = True) -> ImportResult:
        result = ImportResult()
        for i, record in enumerate(records):
            product, status = self.import_record(record)
            if product is None:
                result.errors.append({"index": i, "error": status})
            elif status == "created":
                result.created.append(product.id)
            elif status == "updated":
                result.updated.append(product.id)
            else:
                result.skipped.append(i)

        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                result.errors.append({"error": f"Commit failed: {str(e)}"})

        return result

    def import_from_json(self, data: list[dict]) -> ImportResult:
        return self.import_batch(data)

    def import_from_csv_rows(self, rows: list[dict]) -> ImportResult:
        """Convert flat CSV rows to nested records and import."""
        records = []
        for row in rows:
            specs = []
            spec_prefix = "spec_"
            product_fields = {}
            taxonomy = {}
            for key, value in row.items():
                if key.startswith(spec_prefix) and value:
                    spec_key = key[len(spec_prefix):]
                    specs.append({"key": spec_key, "value": value, "group_name": "General"})
                elif key in ("category", "manufacturer", "family", "series", "generation", "architecture"):
                    taxonomy[key] = value
                else:
                    product_fields[key] = value
            product_fields["specifications"] = specs
            records.append({**taxonomy, "product": product_fields})
        return self.import_batch(records)
