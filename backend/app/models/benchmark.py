from datetime import datetime, timezone

from app import db


class Benchmark(db.Model):
    __tablename__ = "benchmarks"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    name = db.Column(db.String(150), nullable=False)
    score = db.Column(db.Float)
    unit = db.Column(db.String(50))
    source = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    product = db.relationship("Product", back_populates="benchmarks")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "unit": self.unit,
            "source": self.source,
            "notes": self.notes,
        }
