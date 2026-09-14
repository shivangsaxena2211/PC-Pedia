from datetime import datetime, timezone

from app import db


class Series(db.Model):
    __tablename__ = "series"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), nullable=False, index=True)
    family_id = db.Column(db.Integer, db.ForeignKey("families.id"), index=True)
    # Legacy columns kept for migration compatibility; prefer family relationship
    manufacturer_id = db.Column(
        db.Integer, db.ForeignKey("manufacturers.id"), index=True
    )
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), index=True)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    family = db.relationship("Family", back_populates="series_list")
    manufacturer = db.relationship("Manufacturer", back_populates="series")
    category = db.relationship("Category")
    generations = db.relationship(
        "Generation", back_populates="series", lazy="dynamic", cascade="all, delete-orphan"
    )
    products = db.relationship("Product", back_populates="series", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("family_id", "slug", name="uq_series_family_slug"),
    )

    def to_dict(self):
        mfr = self.family.manufacturer if self.family else self.manufacturer
        cat = self.family.category if self.family else self.category
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "family_id": self.family_id,
            "family": self.family.name if self.family else None,
            "family_slug": self.family.slug if self.family else None,
            "manufacturer_id": mfr.id if mfr else self.manufacturer_id,
            "manufacturer": mfr.name if mfr else None,
            "manufacturer_slug": mfr.slug if mfr else None,
            "category_id": cat.id if cat else self.category_id,
            "category_slug": cat.slug if cat else None,
            "description": self.description,
            "display_order": self.display_order,
        }
