from datetime import datetime, timezone

from app import db

PRODUCT_STATUSES = ("active", "draft", "discontinued")


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False, index=True)
    manufacturer_id = db.Column(
        db.Integer, db.ForeignKey("manufacturers.id"), nullable=False, index=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    family_id = db.Column(db.Integer, db.ForeignKey("families.id"), index=True)
    series_id = db.Column(db.Integer, db.ForeignKey("series.id"), index=True)
    generation_id = db.Column(db.Integer, db.ForeignKey("generations.id"), index=True)
    architecture = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default="active", nullable=False, index=True)
    is_popular = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    manufacturer = db.relationship("Manufacturer", back_populates="products")
    category = db.relationship("Category", back_populates="products")
    family = db.relationship("Family", back_populates="products")
    series = db.relationship("Series", back_populates="products")
    generation = db.relationship("Generation", back_populates="products")
    specifications = db.relationship(
        "Specification",
        back_populates="product",
        lazy="joined",
        cascade="all, delete-orphan",
        order_by="Specification.sort_order",
    )
    images = db.relationship(
        "ProductImage",
        back_populates="product",
        lazy="joined",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )
    benchmarks = db.relationship(
        "Benchmark",
        back_populates="product",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "category_id", "manufacturer_id", "slug", name="uq_product_category_mfr_slug"
        ),
        db.Index("ix_product_category_slug", "category_id", "slug"),
    )

    def to_dict(
        self,
        include_specs=False,
        include_images=False,
        include_benchmarks=False,
        list_view=False,
    ):
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "manufacturer_id": self.manufacturer_id,
            "manufacturer": self.manufacturer.name if self.manufacturer else None,
            "manufacturer_slug": self.manufacturer.slug if self.manufacturer else None,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "category_slug": self.category.slug if self.category else None,
            "family_id": self.family_id,
            "family": self.family.name if self.family else None,
            "family_slug": self.family.slug if self.family else None,
            "series_id": self.series_id,
            "series": self.series.name if self.series else None,
            "series_slug": self.series.slug if self.series else None,
            "generation_id": self.generation_id,
            "generation": self.generation.name if self.generation else None,
            "generation_slug": self.generation.slug if self.generation else None,
            "architecture": self.architecture,
            "description": self.description,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "image_url": self.image_url,
            "primary_image_url": self.primary_image_url,
            "status": self.status,
            "is_popular": self.is_popular,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if list_view and self.specifications:
            data["quick_specs"] = {
                s.key: s.value for s in self.specifications[:6]
            }

        if include_specs:
            data["specifications"] = [s.to_dict() for s in self.specifications]
        if include_images:
            data["images"] = [i.to_dict() for i in self.images]
        if include_benchmarks:
            data["benchmarks"] = [b.to_dict() for b in self.benchmarks]

        return data

    @property
    def primary_image_url(self):
        """Resolve the best available product-specific image URL."""
        if self.image_url and self.image_url.strip():
            return self.image_url.strip()
        for img in sorted(self.images, key=lambda i: (not i.is_primary, i.sort_order)):
            if img.url and img.url.strip():
                return img.url.strip()
        return None

    @property
    def url_path(self):
        cat = self.category.slug if self.category else "product"
        mfr = self.manufacturer.slug if self.manufacturer else "unknown"
        return f"/{cat}/{mfr}/{self.slug}"
