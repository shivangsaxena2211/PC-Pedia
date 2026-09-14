"""Helpers for resolving product image URLs."""


def resolve_primary_image_url(image_url: str | None, images: list) -> str | None:
    """
    Resolve the best product-specific image URL.

    Priority:
      1. ProductImage marked primary
      2. First valid ProductImage (by sort_order)
      3. Product.image_url
    """
    for img in images:
        if img.is_primary and img.url and img.url.strip():
            return img.url.strip()

    for img in sorted(images, key=lambda i: (i.sort_order, i.id)):
        if img.url and img.url.strip():
            return img.url.strip()

    if image_url and image_url.strip():
        return image_url.strip()

    return None
