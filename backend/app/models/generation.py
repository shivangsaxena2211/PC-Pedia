from datetime import datetime, timezone

from app import db


class Generation(db.Model):
    __tablename__ = "generations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), nullable=False, index=True)
    series_id = db.Column(
        db.Integer, db.ForeignKey("series.id"), nullable=False, index=True
    )
    architecture = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    series = db.relationship("Series", back_populates="generations")
    products = db.relationship("Product", back_populates="generation", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("series_id", "slug", name="uq_generation_series_slug"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "series_id": self.series_id,
            "series": self.series.name if self.series else None,
            "series_slug": self.series.slug if self.series else None,
            "architecture": self.architecture,
            "release_year": self.release_year,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "description": self.description,
            "display_order": self.display_order,
        }
