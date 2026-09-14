from app.models.product import Product


def product_list_item(product: Product) -> dict:
    return product.to_dict()


def product_detail(product: Product) -> dict:
    return product.to_dict(
        include_specs=True,
        include_images=True,
        include_benchmarks=True,
    )


def grouped_specifications(product: Product) -> dict:
    groups = {}
    for spec in product.specifications:
        group = spec.group_name or "General"
        if group not in groups:
            groups[group] = []
        groups[group].append(spec.to_dict())
    return groups
