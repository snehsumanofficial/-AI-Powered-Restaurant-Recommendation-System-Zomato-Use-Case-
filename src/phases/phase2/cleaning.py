from __future__ import annotations

import hashlib
from typing import Any

from src.phases.phase2.models import Restaurant


def derive_cost_tier(cost_for_two: float | None) -> str | None:
    if cost_for_two is None:
        return None
    if cost_for_two <= 800:
        return "low"
    if cost_for_two <= 2000:
        return "medium"
    return "high"


def parse_cuisines(cuisine_value: Any) -> list[str]:
    if cuisine_value is None:
        return []
    if isinstance(cuisine_value, list):
        parsed = [str(item).strip().lower() for item in cuisine_value if str(item).strip()]
    else:
        parsed = [part.strip().lower() for part in str(cuisine_value).split(",") if part.strip()]
    return sorted(set(parsed))


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "null", "NULL"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_present(raw: dict[str, Any], candidates: list[str]) -> Any:
    for key in candidates:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def normalize_row(raw: dict[str, Any], row_index: int) -> Restaurant | None:
    name = _first_present(raw, ["name", "restaurant_name", "Restaurant Name"])
    location = _first_present(raw, ["location", "city", "Locality", "Address"])
    if not name or not location:
        return None

    cuisine_value = _first_present(raw, ["cuisines", "Cuisine", "Cuisines"])
    cost_value = _first_present(raw, ["cost_for_two", "average_cost_for_two", "Average Cost for two"])
    rating_value = _first_present(raw, ["rating", "aggregate_rating", "Aggregate rating"])

    cuisines = parse_cuisines(cuisine_value)
    cost_for_two = _safe_float(cost_value)
    rating = _safe_float(rating_value)
    if rating is not None:
        rating = max(0.0, min(5.0, rating))

    stable_key = f"{name}|{location}|{row_index}"
    rid = hashlib.sha1(stable_key.encode("utf-8")).hexdigest()[:16]

    return Restaurant(
        id=rid,
        name=str(name).strip(),
        location=str(location).strip().lower(),
        cuisines=cuisines,
        cost_for_two=cost_for_two,
        cost_tier=derive_cost_tier(cost_for_two),
        rating=rating,
        raw=dict(raw),
    )
