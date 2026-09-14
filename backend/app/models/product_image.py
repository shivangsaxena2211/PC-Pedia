from app import db

IMAGE_TYPES = (
    "primary",
    "front",
    "back",
    "side",
    "installed",
    "diagram",
    "thumbnail",
)


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255))
    image_type = db.Column(db.String(50), default="primary", index=True)
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)

    product = db.relationship("Product", back_populates="images")

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "alt_text": self.alt_text,
            "image_type": self.image_type,
            "is_primary": self.is_primary,
            "sort_order": self.sort_order,
        }
