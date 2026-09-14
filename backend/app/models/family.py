from datetime import datetime, timezone

from app import db


class Family(db.Model):
    __tablename__ = "families"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), nullable=False, index=True)
    manufacturer_id = db.Column(
        db.Integer, db.ForeignKey("manufacturers.id"), nullable=False, index=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    manufacturer = db.relationship("Manufacturer", back_populates="families")
    category = db.relationship("Category", back_populates="families")
    series_list = db.relationship(
        "Series", back_populates="family", lazy="dynamic", cascade="all, delete-orphan"
    )
    products = db.relationship("Product", back_populates="family", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint(
            "category_id", "manufacturer_id", "slug", name="uq_family_category_mfr_slug"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "manufacturer_id": self.manufacturer_id,
            "manufacturer": self.manufacturer.name if self.manufacturer else None,
            "manufacturer_slug": self.manufacturer.slug if self.manufacturer else None,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "category_slug": self.category.slug if self.category else None,
            "description": self.description,
            "display_order": self.display_order,
        }
