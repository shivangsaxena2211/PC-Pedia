from datetime import datetime, timezone

from app import db


class ProductSource(db.Model):
    __tablename__ = "product_sources"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    source_id = db.Column(
        db.Integer, db.ForeignKey("data_sources.id"), nullable=False, index=True
    )
    source_url = db.Column(db.String(500))
    source_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    product = db.relationship("Product", back_populates="product_sources")
    source = db.relationship("DataSource", back_populates="product_sources")

    __table_args__ = (
        db.UniqueConstraint(
            "product_id", "source_id", "source_url", name="uq_product_source_link"
        ),
    )

    def to_dict(self):
        data = {
            "id": self.id,
            "product_id": self.product_id,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "source_date": self.source_date.isoformat() if self.source_date else None,
            "notes": self.notes,
        }
        if self.source:
            data["source"] = self.source.to_dict()
        return data
