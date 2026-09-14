from app import db

DATA_TYPES = ("string", "integer", "decimal", "boolean", "date", "enum")


class SpecificationDefinition(db.Model):
    __tablename__ = "specification_definitions"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    group_name = db.Column(db.String(100), nullable=False, default="General")
    key = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(150), nullable=False)
    data_type = db.Column(db.String(20), nullable=False, default="string")
    unit = db.Column(db.String(50))
    filterable = db.Column(db.Boolean, default=False, index=True)
    comparable = db.Column(db.Boolean, default=True)
    required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    enum_values = db.Column(db.Text)  # JSON array for enum type

    category = db.relationship("Category", back_populates="specification_definitions")

    __table_args__ = (
        db.UniqueConstraint("category_id", "key", name="uq_spec_def_category_key"),
        db.Index("ix_spec_def_category_group", "category_id", "group_name"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "group_name": self.group_name,
            "key": self.key,
            "display_name": self.display_name,
            "data_type": self.data_type,
            "unit": self.unit,
            "filterable": self.filterable,
            "comparable": self.comparable,
            "required": self.required,
            "display_order": self.display_order,
            "enum_values": self.enum_values,
        }
