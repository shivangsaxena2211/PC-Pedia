from app import db


class Specification(db.Model):
    __tablename__ = "specifications"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    group_name = db.Column(db.String(100), nullable=False, default="General")
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)
    unit = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)

    product = db.relationship("Product", back_populates="specifications")
    specification_sources = db.relationship(
        "SpecificationSource",
        back_populates="specification",
        lazy="select",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.Index("ix_spec_product_group_key", "product_id", "group_name", "key"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
            "key": self.key,
            "value": self.value,
            "unit": self.unit,
            "sort_order": self.sort_order,
        }
