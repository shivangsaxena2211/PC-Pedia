"""Known invalid manufacturer/category/family combinations for import validation."""

from app.utils.helpers import slugify

# Families that must NOT be used with a given (manufacturer_slug, category_slug).
INVALID_FAMILY_SLUGS: dict[tuple[str, str], set[str]] = {
    ("amd", "cpu"): {"core", "pentium", "celeron", "xeon", "atom"},
    ("intel", "cpu"): {"ryzen", "epyc", "threadripper", "fx", "athlon", "phenom"},
    ("nvidia", "gpu"): {"radeon", "arc", "radeon-rx"},
    ("amd", "gpu"): {"geforce", "arc", "geforce-rtx", "geforce-gtx"},
    ("intel", "gpu"): {"geforce", "radeon", "radeon-rx", "geforce-rtx"},
}

# Category slug aliases accepted in import records.
CATEGORY_ALIASES: dict[str, str] = {
    "cpu": "cpu",
    "cpus": "cpu",
    "gpu": "gpu",
    "gpus": "gpu",
    "ram": "ram",
    "memory": "ram",
    "motherboard": "motherboards",
    "motherboards": "motherboards",
    "ssd": "ssd",
    "ssds": "ssd",
    "psu": "psu",
    "psus": "psu",
    "power supply": "psu",
    "cooler": "coolers",
    "coolers": "coolers",
    "cpu cooler": "coolers",
    "aio": "aio",
    "aios": "aio",
    "liquid cooler": "aio",
    "fan": "fans",
    "fans": "fans",
    "case": "cases",
    "cases": "cases",
}


def normalize_category_slug(value: str) -> str:
    return CATEGORY_ALIASES.get(value.strip().lower(), slugify(value))


def validate_family_for_manufacturer(
    manufacturer_slug: str,
    category_slug: str,
    family_name: str,
) -> str | None:
    """Return an error message if the family is invalid for this manufacturer/category."""
    family_slug = slugify(family_name)
    denied = INVALID_FAMILY_SLUGS.get((manufacturer_slug, category_slug), set())
    if family_slug in denied:
        return (
            f"Family '{family_name}' is not valid for manufacturer "
            f"'{manufacturer_slug}' in category '{category_slug}'"
        )
    for denied_slug in denied:
        if denied_slug in family_slug or family_slug in denied_slug:
            return (
                f"Family '{family_name}' appears incompatible with manufacturer "
                f"'{manufacturer_slug}' in category '{category_slug}'"
            )
    return None
