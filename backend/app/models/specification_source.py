from datetime import datetime, timezone

from app import db


class SpecificationSource(db.Model):
    __tablename__ = "specification_sources"

    id = db.Column(db.Integer, primary_key=True)
    specification_id = db.Column(
        db.Integer, db.ForeignKey("specifications.id"), nullable=False, index=True
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

    specification = db.relationship(
        "Specification", back_populates="specification_sources"
    )
    source = db.relationship("DataSource", back_populates="specification_sources")

    __table_args__ = (
        db.UniqueConstraint(
            "specification_id",
            "source_id",
            "source_url",
            name="uq_specification_source_link",
        ),
    )

    def to_dict(self):
        data = {
            "id": self.id,
            "specification_id": self.specification_id,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "source_date": self.source_date.isoformat() if self.source_date else None,
            "notes": self.notes,
        }
        if self.source:
            data["source"] = self.source.to_dict()
        return data
