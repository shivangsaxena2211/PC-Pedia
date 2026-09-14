"""Normalize imported specification values according to SpecificationDefinition types."""

import json
import re
from datetime import datetime

from app.models.specification_definition import DATA_TYPES


def _strip_unit_suffix(value: str, unit: str | None) -> str:
    if not unit:
        return value.strip()
    pattern = re.compile(rf"\s*{re.escape(unit)}\s*$", re.IGNORECASE)
    return pattern.sub("", value).strip()


def normalize_spec_entry(defn, raw_value, raw_unit=None) -> tuple[str, str | None, list[str]]:
    """
    Normalize a specification value/unit pair.

    Returns (value, unit, warnings).
    """
    warnings: list[str] = []
    if raw_value is None:
        return "", raw_unit, warnings

    value = str(raw_value).strip()
    unit = raw_unit.strip() if raw_unit else None
    data_type = defn.data_type if defn else "string"

    if data_type not in DATA_TYPES:
        data_type = "string"

    if data_type == "integer":
        cleaned = value.replace(",", "")
        match = re.search(r"-?\d+", cleaned)
        if not match:
            raise ValueError(f"Expected integer, got '{value}'")
        normalized = match.group(0)
        if normalized != cleaned and cleaned != normalized:
            warnings.append(f"Normalized integer '{value}' to '{normalized}'")
        return normalized, unit or (defn.unit if defn else None), warnings

    if data_type == "decimal":
        cleaned = _strip_unit_suffix(value, unit or (defn.unit if defn else None))
        cleaned = cleaned.replace(",", "")
        match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
        if not match:
            raise ValueError(f"Expected decimal number, got '{value}'")
        normalized = match.group(0)
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".") if "." in normalized else normalized
            if normalized.endswith("."):
                normalized += "0"
        return normalized, unit or (defn.unit if defn else None), warnings

    if data_type == "boolean":
        lowered = value.lower()
        mapping = {
            "true": "true",
            "yes": "true",
            "1": "true",
            "false": "false",
            "no": "false",
            "0": "false",
        }
        if lowered not in mapping:
            raise ValueError(f"Expected boolean, got '{value}'")
        return mapping[lowered], unit, warnings

    if data_type == "date":
        try:
            parsed = datetime.fromisoformat(value[:10])
        except ValueError:
            raise ValueError(f"Expected date (YYYY-MM-DD), got '{value}'")
        return parsed.date().isoformat(), unit, warnings

    if data_type == "enum" and defn and defn.enum_values:
        try:
            allowed = json.loads(defn.enum_values)
        except json.JSONDecodeError:
            allowed = []
        if allowed and value not in allowed:
            # Case-insensitive enum match
            match = next((item for item in allowed if str(item).lower() == value.lower()), None)
            if match is None:
                raise ValueError(
                    f"Expected one of [{', '.join(allowed)}], got '{value}'"
                )
            if str(match) != value:
                warnings.append(f"Normalized enum '{value}' to '{match}'")
            return str(match), unit, warnings

    # string and fallback
    if unit and defn and defn.unit and not unit:
        unit = defn.unit
    return value, unit or (defn.unit if defn else None), warnings
