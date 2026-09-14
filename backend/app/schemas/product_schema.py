from sqlalchemy.orm import joinedload

from app.models.product import Product
from app.models.product_source import ProductSource


def product_list_item(product: Product) -> dict:
    return product.to_dict()


def product_detail(product: Product) -> dict:
    return product.to_dict(
        include_specs=True,
        include_images=True,
        include_benchmarks=True,
        include_sources=True,
    )


def grouped_specifications(product: Product) -> dict:
    from app.models import SpecificationDefinition

    definitions = {
        d.key: d
        for d in SpecificationDefinition.query.filter_by(
            category_id=product.category_id
        ).all()
    }

    groups = {}
    for spec in product.specifications:
        group = spec.group_name or "General"
        if group not in groups:
            groups[group] = []
        payload = spec.to_dict()
        defn = definitions.get(spec.key)
        if defn:
            payload["display_name"] = defn.display_name
        groups[group].append(payload)
    return groups


def load_product_detail(product_id: int | None = None, product: Product | None = None):
    """Load a product with sources for detail responses."""
    if product is None and product_id is not None:
        product = (
            Product.query.options(
                joinedload(Product.product_sources).joinedload(ProductSource.source),
            )
            .filter_by(id=product_id)
            .first()
        )
    return product
