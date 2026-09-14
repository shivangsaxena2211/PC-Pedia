"""
Hardware data ingestion service for JSON/CSV import.

Usage:
    from app.services.import_service import import_hardware, ImportMode

    result = import_hardware(records, mode=ImportMode.UPSERT)
    result = import_hardware(records, mode=ImportMode.CREATE, dry_run=True)
"""

from __future__ import annotations

import csv
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from app import db
from app.data.taxonomy_rules import (
    normalize_category_slug,
    validate_family_for_manufacturer,
)
from app.models import (
    Benchmark,
    Category,
    Family,
    Generation,
    Manufacturer,
    Product,
    ProductImage,
    Series,
    Specification,
    SpecificationDefinition,
)
from app.models.product_image import IMAGE_TYPES
from app.services.source_service import (
    upsert_product_source,
    upsert_specification_sources,
)
from app.utils.helpers import parse_bool, slugify
from app.utils.spec_normalizer import normalize_spec_entry

logger = logging.getLogger("pc_pedia.import")

FALLBACK_IMAGE_PREFIX = "/images/hardware/"
HTTP_URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


class ImportMode(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    UPSERT = "upsert"


@dataclass
class RecordImportResult:
    product: str
    status: str
    product_id: int | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    is_new: bool = False


@dataclass
class ImportBatchResult:
    total: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    warnings: int = 0
    files_processed: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    existing_records: int = 0
    new_records: int = 0
    details: list[RecordImportResult] = field(default_factory=list)
    dry_run: bool = False

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "errors": self.errors,
            "warnings": self.warnings,
            "files_processed": self.files_processed,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "existing_records": self.existing_records,
            "new_records": self.new_records,
            "dry_run": self.dry_run,
            "details": [
                {
                    "product": d.product,
                    "status": d.status,
                    "product_id": d.product_id,
                    "errors": d.errors,
                    "warnings": d.warnings,
                    "actions": d.actions,
                }
                for d in self.details
            ],
        }


class HardwareImportService:
    """Import structured hardware records into taxonomy + product tables."""

    def __init__(
        self,
        mode: ImportMode = ImportMode.UPSERT,
        dry_run: bool = False,
        replace_specifications: bool = False,
        replace_images: bool = False,
    ):
        self.mode = mode
        self.dry_run = dry_run
        self.replace_specifications = replace_specifications
        self.replace_images = replace_images

    # ─── Record normalization ────────────────────────────────────────────────

    @staticmethod
    def normalize_record(record: dict) -> dict:
        """Accept standard format and legacy nested variants."""
        normalized = dict(record)
        product = dict(normalized.get("product") or {})

        if normalized.get("specifications") and not product.get("specifications"):
            product["specifications"] = normalized["specifications"]
        if normalized.get("images") and not product.get("images"):
            product["images"] = normalized["images"]
        if normalized.get("benchmarks") and not product.get("benchmarks"):
            product["benchmarks"] = normalized["benchmarks"]
        if normalized.get("image_url") and not product.get("image_url"):
            product["image_url"] = normalized["image_url"]

        normalized["product"] = product
        return normalized

    @staticmethod
    def load_records_from_file(path: str) -> list[dict]:
        import os

        if os.path.isdir(path):
            records: list[dict] = []
            for root, _, files in os.walk(path):
                for filename in sorted(files):
                    if filename.lower().endswith((".json", ".csv")):
                        file_path = os.path.join(root, filename)
                        records.extend(HardwareImportService.load_records_from_file(file_path))
            return records

        if path.lower().endswith(".json"):
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return [data]
            if not isinstance(data, list):
                raise ValueError("JSON import file must contain an object or array")
            return data
        if path.lower().endswith(".csv"):
            return HardwareImportService.load_records_from_csv(path)
        raise ValueError(f"Unsupported file format: {path}")

    @staticmethod
    def count_import_files(path: str) -> int:
        import os

        if os.path.isdir(path):
            count = 0
            for _, _, files in os.walk(path):
                count += sum(
                    1 for filename in files
                    if filename.lower().endswith((".json", ".csv"))
                )
            return count
        return 1

    @staticmethod
    def load_records_from_csv(path: str) -> list[dict]:
        records = []
        with open(path, encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                records.append(HardwareImportService.csv_row_to_record(row))
        return records

    @staticmethod
    def csv_row_to_record(row: dict) -> dict:
        specs = []
        if row.get("specifications_json"):
            specs = json.loads(row["specifications_json"])
        else:
            for key, value in row.items():
                if key.startswith("spec_") and value:
                    specs.append({
                        "group": "General",
                        "key": key[5:],
                        "value": value,
                    })

        images = []
        if row.get("images_json"):
            images = json.loads(row["images_json"])
        elif row.get("image_url"):
            images = [{
                "url": row["image_url"],
                "type": "primary",
                "is_primary": True,
                "sort_order": 1,
            }]

        product = {
            "name": row.get("name", "").strip(),
            "slug": row.get("slug", "").strip() or None,
            "description": row.get("description") or None,
            "release_date": row.get("release_date") or None,
            "status": row.get("status") or "active",
            "is_popular": parse_bool(row.get("is_popular")),
            "architecture": row.get("architecture") or None,
            "image_url": row.get("image_url") or None,
            "specifications": specs,
            "images": images,
        }

        return {
            "category": row.get("category", "").strip(),
            "manufacturer": row.get("manufacturer", "").strip(),
            "family": row.get("family", "").strip() or None,
            "series": row.get("series", "").strip() or None,
            "generation": row.get("generation", "").strip() or None,
            "architecture": row.get("architecture") or None,
            "source": HardwareImportService._parse_source(row),
            "product": product,
            "specifications": specs,
            "images": images,
        }

    @staticmethod
    def _parse_source(row: dict) -> dict | None:
        if not any(row.get(k) for k in ("source_name", "source_url", "source_date")):
            return None
        return {
            "name": row.get("source_name"),
            "url": row.get("source_url"),
            "date": row.get("source_date"),
        }

    # ─── Taxonomy resolution ───────────────────────────────────────────────────

    def resolve_category(self, slug_or_name: str) -> Category | None:
        slug = normalize_category_slug(slug_or_name)
        return Category.query.filter(
            db.or_(Category.slug == slug, Category.name.ilike(slug_or_name.strip()))
        ).first()

    def resolve_or_create_manufacturer(self, name: str) -> Manufacturer:
        slug = slugify(name)
        mfr = Manufacturer.query.filter(
            db.or_(Manufacturer.slug == slug, Manufacturer.name.ilike(name.strip()))
        ).first()
        if mfr:
            return mfr
        mfr = Manufacturer(name=name.strip(), slug=slug)
        db.session.add(mfr)
        db.session.flush()
        logger.info("[CREATE] Manufacturer: %s", name)
        return mfr

    def resolve_or_create_family(
        self, name: str, manufacturer: Manufacturer, category: Category
    ) -> Family:
        error = validate_family_for_manufacturer(
            manufacturer.slug, category.slug, name
        )
        if error:
            raise ValueError(error)

        slug = slugify(name)
        family = Family.query.filter_by(
            category_id=category.id,
            manufacturer_id=manufacturer.id,
            slug=slug,
        ).first()
        if family:
            return family

        family = Family.query.filter(
            Family.slug == slug,
            db.or_(
                Family.manufacturer_id != manufacturer.id,
                Family.category_id != category.id,
            ),
        ).first()
        if family:
            raise ValueError(
                f"Family '{name}' already exists for a different manufacturer/category"
            )

        family = Family(
            name=name.strip(),
            slug=slug,
            manufacturer_id=manufacturer.id,
            category_id=category.id,
        )
        db.session.add(family)
        db.session.flush()
        logger.info("[CREATE] Family: %s", name)
        return family

    def resolve_or_create_series(self, name: str, family: Family) -> Series:
        slug = slugify(name)
        series = Series.query.filter_by(family_id=family.id, slug=slug).first()
        if series:
            if series.manufacturer_id != family.manufacturer_id:
                raise ValueError(
                    f"Series '{name}' belongs to a different manufacturer"
                )
            if series.category_id != family.category_id:
                raise ValueError(
                    f"Series '{name}' belongs to a different category"
                )
            return series

        series = Series(
            name=name.strip(),
            slug=slug,
            family_id=family.id,
            manufacturer_id=family.manufacturer_id,
            category_id=family.category_id,
        )
        db.session.add(series)
        db.session.flush()
        logger.info("[CREATE] Series: %s", name)
        return series

    def resolve_or_create_generation(self, name: str, series: Series) -> Generation | None:
        if not name:
            return None
        slug = slugify(name)
        generation = Generation.query.filter_by(series_id=series.id, slug=slug).first()
        if generation:
            return generation
        generation = Generation(name=name.strip(), slug=slug, series_id=series.id)
        db.session.add(generation)
        db.session.flush()
        logger.info("[CREATE] Generation: %s", name)
        return generation

    # ─── Validation helpers ──────────────────────────────────────────────────

    @staticmethod
    def _validate_url(url: str) -> str | None:
        if not url or not url.strip():
            return "Image URL is required"
        url = url.strip()
        if url.startswith(FALLBACK_IMAGE_PREFIX):
            return "Generic fallback SVG URLs must not be stored as product images"
        if not HTTP_URL_PATTERN.match(url):
            return f"Invalid image URL: {url}"
        parsed = urlparse(url)
        if not parsed.netloc:
            return f"Invalid image URL: {url}"
        return None

    def validate_images(self, images: list[dict], product_name: str) -> tuple[list[dict], list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        if not images:
            warnings.append("No product images provided; frontend will use category fallback")
            return [], warnings, errors

        primary_count = sum(1 for img in images if img.get("is_primary"))
        if primary_count > 1:
            errors.append("Multiple images marked as primary; only one primary image is allowed")

        seen_urls: set[str] = set()
        validated: list[dict] = []

        for index, image in enumerate(images):
            url = (image.get("url") or "").strip()
            url_error = self._validate_url(url)
            if url_error:
                errors.append(f"Image {index + 1}: {url_error}")
                continue
            if url in seen_urls:
                errors.append(f"Image {index + 1}: duplicate URL '{url}'")
                continue
            seen_urls.add(url)

            image_type = image.get("type") or image.get("image_type") or "primary"
            if image_type not in IMAGE_TYPES:
                errors.append(
                    f"Image {index + 1}: invalid type '{image_type}'. "
                    f"Allowed: {', '.join(IMAGE_TYPES)}"
                )
                continue

            validated.append({
                "url": url,
                "alt_text": image.get("alt_text") or product_name,
                "image_type": image_type,
                "is_primary": bool(image.get("is_primary", image_type == "primary")),
                "sort_order": int(image.get("sort_order") or index + 1),
            })

        if validated and not any(img["is_primary"] for img in validated):
            validated[0]["is_primary"] = True
            validated[0]["image_type"] = "primary"

        return validated, warnings, errors

    def normalize_and_validate_specs(
        self, category_id: int, specs: list[dict]
    ) -> tuple[list[dict], list[str], list[str]]:
        definitions = SpecificationDefinition.query.filter_by(category_id=category_id).all()
        def_map = {d.key: d for d in definitions}
        errors: list[str] = []
        warnings: list[str] = []
        normalized_specs: list[dict] = []

        for spec in specs:
            key = spec.get("key")
            if not key:
                errors.append("Specification missing key")
                continue
            if spec.get("value") is None or str(spec.get("value")).strip() == "":
                defn = def_map.get(key)
                if defn and defn.required:
                    errors.append(f"Required specification '{key}' is empty")
                else:
                    warnings.append(f"Optional specification '{key}' is empty")
                continue

            defn = def_map.get(key)
            if not defn:
                warnings.append(f"No specification definition for '{key}' in this category")
                try:
                    normalized_specs.append({
                        "group_name": spec.get("group") or spec.get("group_name") or "General",
                        "key": key,
                        "value": str(spec.get("value")),
                        "unit": spec.get("unit"),
                        "sort_order": spec.get("sort_order", len(normalized_specs)),
                    })
                except ValueError as exc:
                    errors.append(str(exc))
                continue

            try:
                value, unit, spec_warnings = normalize_spec_entry(
                    defn, spec.get("value"), spec.get("unit")
                )
                warnings.extend(spec_warnings)
                normalized_specs.append({
                    "group_name": spec.get("group") or spec.get("group_name") or defn.group_name,
                    "key": key,
                    "value": value,
                    "unit": unit,
                    "sort_order": spec.get("sort_order", defn.display_order),
                })
            except ValueError as exc:
                errors.append(f"{key}: {exc}")

        return normalized_specs, warnings, errors

    # ─── Persistence helpers ───────────────────────────────────────────────────

    def _upsert_specifications(self, product: Product, specs: list[dict]) -> list[int]:
        if self.replace_specifications:
            Specification.query.filter_by(product_id=product.id).delete()

        existing = {
            spec.key: spec
            for spec in Specification.query.filter_by(product_id=product.id).all()
        }
        spec_ids: list[int] = []

        for index, spec in enumerate(specs):
            key = spec["key"]
            if key in existing:
                row = existing[key]
                row.group_name = spec.get("group_name") or row.group_name
                row.value = spec["value"]
                row.unit = spec.get("unit")
                row.sort_order = spec.get("sort_order", index)
                spec_ids.append(row.id)
            else:
                row = Specification(
                    product_id=product.id,
                    group_name=spec.get("group_name") or "General",
                    key=key,
                    value=spec["value"],
                    unit=spec.get("unit"),
                    sort_order=spec.get("sort_order", index),
                )
                db.session.add(row)
                db.session.flush()
                spec_ids.append(row.id)

        return spec_ids

    def _upsert_images(self, product: Product, images: list[dict]):
        if self.replace_images:
            ProductImage.query.filter_by(product_id=product.id).delete()

        existing_by_url = {
            img.url: img
            for img in ProductImage.query.filter_by(product_id=product.id).all()
        }

        for image in images:
            current = existing_by_url.get(image["url"])
            if current:
                current.alt_text = image.get("alt_text")
                current.image_type = image["image_type"]
                current.is_primary = image.get("is_primary", False)
                current.sort_order = image.get("sort_order", 0)
            else:
                db.session.add(ProductImage(
                    product_id=product.id,
                    url=image["url"],
                    alt_text=image.get("alt_text"),
                    image_type=image["image_type"],
                    is_primary=image.get("is_primary", False),
                    sort_order=image.get("sort_order", 0),
                ))

        if images:
            primary_url = next(
                (img["url"] for img in images if img.get("is_primary")),
                images[0]["url"],
            )
            product.image_url = primary_url

    def _upsert_benchmarks(self, product: Product, benchmarks: list[dict]):
        if not benchmarks:
            return
        for bench in benchmarks:
            if not bench.get("name"):
                continue
            existing = Benchmark.query.filter_by(
                product_id=product.id, name=bench["name"]
            ).first()
            if existing:
                existing.score = bench.get("score")
                existing.unit = bench.get("unit")
                existing.source = bench.get("source")
                existing.notes = bench.get("notes")
            else:
                db.session.add(Benchmark(
                    product_id=product.id,
                    name=bench["name"],
                    score=bench.get("score"),
                    unit=bench.get("unit"),
                    source=bench.get("source"),
                    notes=bench.get("notes"),
                ))

    # ─── Single record import ──────────────────────────────────────────────────

    def import_record(self, record: dict) -> RecordImportResult:
        record = self.normalize_record(record)
        product_data = record.get("product") or {}
        product_name = product_data.get("name") or "Unknown product"
        result = RecordImportResult(product=product_name, status="error")

        logger.info("[IMPORT] %s", product_name)

        try:
            if not record.get("category"):
                raise ValueError("Missing category")
            if not record.get("manufacturer"):
                raise ValueError("Missing manufacturer")
            if not product_data.get("name"):
                raise ValueError("Missing product name")

            category = self.resolve_category(record["category"])
            if not category:
                raise ValueError(f"Invalid category: {record['category']}")

            manufacturer = self.resolve_or_create_manufacturer(record["manufacturer"])
            family_name = record.get("family") or record.get("series")
            series_name = record.get("series") or record.get("family")
            if not family_name or not series_name:
                raise ValueError("Family and series are required for taxonomy resolution")

            family = self.resolve_or_create_family(family_name, manufacturer, category)
            series = self.resolve_or_create_series(series_name, family)
            generation = self.resolve_or_create_generation(record.get("generation"), series)

            slug = product_data.get("slug") or slugify(product_data["name"])
            existing = Product.query.filter_by(
                category_id=category.id,
                manufacturer_id=manufacturer.id,
                slug=slug,
            ).first()

            result.is_new = existing is None

            if existing and self.mode == ImportMode.CREATE:
                result.status = "skipped"
                result.warnings.append("Product already exists (CREATE mode)")
                result.actions.append("SKIP existing product")
                logger.warning("[SKIP] %s already exists", product_name)
                return result

            specs = (
                record.get("specifications")
                or product_data.get("specifications")
                or []
            )
            normalized_specs, spec_warnings, spec_errors = self.normalize_and_validate_specs(
                category.id, specs
            )
            result.warnings.extend(spec_warnings)
            if spec_errors:
                raise ValueError("; ".join(spec_errors))

            images = record.get("images") or product_data.get("images") or []
            if product_data.get("image_url") and not images:
                images = [{
                    "url": product_data["image_url"],
                    "type": "primary",
                    "is_primary": True,
                    "sort_order": 1,
                }]
            validated_images, image_warnings, image_errors = self.validate_images(
                images, product_name
            )
            result.warnings.extend(image_warnings)
            if image_errors:
                raise ValueError("; ".join(image_errors))

            release_date = product_data.get("release_date")
            if release_date:
                try:
                    release_date = datetime.strptime(str(release_date)[:10], "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Invalid release_date: {release_date}")
            elif not product_data.get("description"):
                result.warnings.append("Missing description")

            benchmarks = record.get("benchmarks") or product_data.get("benchmarks") or []

            source = record.get("source")
            if source:
                result.actions.append(
                    f"SOURCE {source.get('name') or 'unknown'} "
                    f"({source.get('url') or 'no url'})"
                )

            if existing:
                existing.name = product_data["name"]
                existing.family_id = family.id
                existing.series_id = series.id
                existing.generation_id = generation.id if generation else None
                existing.architecture = product_data.get("architecture") or record.get("architecture")
                existing.description = product_data.get("description")
                existing.release_date = release_date
                existing.status = product_data.get("status", existing.status or "active")
                existing.is_popular = product_data.get("is_popular", existing.is_popular)
                product = existing
                result.status = "updated"
                result.actions.extend(["UPDATE product", "UPDATE specifications"])
                logger.info("[UPDATE] Product: %s", product_name)
            else:
                product = Product(
                    name=product_data["name"],
                    slug=slug,
                    category_id=category.id,
                    manufacturer_id=manufacturer.id,
                    family_id=family.id,
                    series_id=series.id,
                    generation_id=generation.id if generation else None,
                    architecture=product_data.get("architecture") or record.get("architecture"),
                    description=product_data.get("description"),
                    release_date=release_date,
                    image_url=product_data.get("image_url"),
                    status=product_data.get("status", "active"),
                    is_popular=product_data.get("is_popular", False),
                )
                db.session.add(product)
                db.session.flush()
                result.status = "created"
                result.actions.extend(["CREATE product", "CREATE specifications"])
                logger.info("[CREATE] Product: %s", product_name)

            spec_ids = self._upsert_specifications(product, normalized_specs)
            if validated_images:
                self._upsert_images(product, validated_images)
                result.actions.append("IMAGE primary/additional images processed")
                logger.info("[IMAGE] Images processed for %s", product_name)
            self._upsert_benchmarks(product, benchmarks)

            if source:
                link = upsert_product_source(product.id, source)
                if link:
                    result.actions.append(f"PERSIST source: {source.get('name')}")
                if spec_ids:
                    upsert_specification_sources(spec_ids, source)

            result.product_id = product.id
            logger.info("[SUCCESS] %s", product_name)
            return result

        except Exception as exc:
            result.errors.append(str(exc))
            result.status = "error"
            logger.error("[ERROR] %s — %s", product_name, exc)
            return result

    def import_batch(
        self,
        records: list[dict],
        files_processed: int = 1,
    ) -> ImportBatchResult:
        batch = ImportBatchResult(
            total=len(records),
            dry_run=self.dry_run,
            files_processed=files_processed,
        )

        for record in records:
            savepoint = db.session.begin_nested()
            detail = self.import_record(record)

            if detail.status == "error":
                savepoint.rollback()
                batch.errors += 1
                batch.invalid_records += 1
            else:
                batch.valid_records += 1
                if detail.is_new:
                    batch.new_records += 1
                else:
                    batch.existing_records += 1

                if self.dry_run:
                    savepoint.rollback()
                else:
                    savepoint.commit()

                if detail.status == "created":
                    batch.created += 1
                elif detail.status == "updated":
                    batch.updated += 1
                elif detail.status == "skipped":
                    batch.skipped += 1

            if detail.warnings:
                batch.warnings += len(detail.warnings)
            batch.details.append(detail)

        if not self.dry_run:
            try:
                db.session.commit()
            except Exception as exc:
                db.session.rollback()
                batch.errors += 1
                batch.details.append(RecordImportResult(
                    product="(batch)",
                    status="error",
                    errors=[f"Commit failed: {exc}"],
                ))

        return batch

    def import_from_json(self, data: list[dict]) -> ImportBatchResult:
        return self.import_batch(data)

    def import_from_csv_rows(self, rows: list[dict]) -> ImportBatchResult:
        records = [self.csv_row_to_record(row) for row in rows]
        return self.import_batch(records)


def import_hardware(
    records: list[dict],
    mode: ImportMode | str = ImportMode.UPSERT,
    dry_run: bool = False,
    replace_specifications: bool = False,
    replace_images: bool = False,
    files_processed: int = 1,
) -> ImportBatchResult:
    """Public API for importing hardware records."""
    if isinstance(mode, str):
        mode = ImportMode(mode.lower())
    service = HardwareImportService(
        mode=mode,
        dry_run=dry_run,
        replace_specifications=replace_specifications,
        replace_images=replace_images,
    )
    normalized = [HardwareImportService.normalize_record(r) for r in records]
    return service.import_batch(normalized, files_processed=files_processed)


def import_hardware_from_path(
    path: str,
    mode: ImportMode | str = ImportMode.UPSERT,
    dry_run: bool = False,
    replace_specifications: bool = False,
    replace_images: bool = False,
) -> ImportBatchResult:
    """Load records from a file or directory and import them."""
    records = HardwareImportService.load_records_from_file(path)
    files_processed = HardwareImportService.count_import_files(path)
    return import_hardware(
        records,
        mode=mode,
        dry_run=dry_run,
        replace_specifications=replace_specifications,
        replace_images=replace_images,
        files_processed=files_processed,
    )


def validate_import_records(records: list[dict]) -> ImportBatchResult:
    """Validate records without modifying the database."""
    return import_hardware(records, dry_run=True)
