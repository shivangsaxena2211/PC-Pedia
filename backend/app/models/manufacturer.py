from datetime import datetime, timezone

from app import db


class Manufacturer(db.Model):
    __tablename__ = "manufacturers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    logo_url = db.Column(db.String(500))
    website = db.Column(db.String(500))
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    families = db.relationship("Family", back_populates="manufacturer", lazy="dynamic")
    series = db.relationship("Series", back_populates="manufacturer", lazy="dynamic")
    products = db.relationship("Product", back_populates="manufacturer", lazy="dynamic")

    def to_dict(self, include_counts=False):
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "logo_url": self.logo_url,
            "website": self.website,
            "description": self.description,
            "display_order": self.display_order,
        }
        if include_counts:
            data["product_count"] = self.products.count()
        return data
