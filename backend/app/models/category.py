from datetime import datetime, timezone

from app import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    display_order = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    products = db.relationship("Product", back_populates="category", lazy="dynamic")
    families = db.relationship("Family", back_populates="category", lazy="dynamic")
    specification_definitions = db.relationship(
        "SpecificationDefinition", back_populates="category", lazy="dynamic"
    )

    def to_dict(self, include_counts=False):
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "display_order": self.display_order,
        }
        if include_counts:
            data["product_count"] = self.products.count()
        return data
