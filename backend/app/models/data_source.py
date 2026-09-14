from datetime import datetime, timezone

from app import db
from app.utils.helpers import slugify


class DataSource(db.Model):
    __tablename__ = "data_sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    url = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    product_sources = db.relationship("ProductSource", back_populates="source")
    specification_sources = db.relationship(
        "SpecificationSource", back_populates="source"
    )

    @staticmethod
    def make_slug(name: str) -> str:
        return slugify(name)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "url": self.url,
            "description": self.description,
        }
