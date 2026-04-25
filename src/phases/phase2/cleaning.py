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
    if value in (None, "", "null", "NULL", "NEW", "-", "NaN", "nan"):
        return None
    try:
        s = str(value).strip().replace(",", "")
        if "/" in s:
            s = s.split("/")[0].strip()
        return float(s)
    except (TypeError, ValueError):
        return None


def _first_present(raw: dict[str, Any], candidates: list[str]) -> Any:
    for key in candidates:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def normalize_row(raw: dict[str, Any], row_index: int) -> Restaurant | None:
    name = _first_present(raw, ["name", "restaurant_name", "Restaurant Name"])
    
    loc_val = _first_present(raw, ["Locality", "locality", "location"])
    city_val = _first_present(raw, ["City", "city", "listed_in(city)"])
    
    if loc_val and city_val and str(loc_val).lower() != str(city_val).lower() and str(city_val).lower() not in str(loc_val).lower():
        location = f"{str(loc_val).strip()}, {str(city_val).strip()}"
    elif loc_val:
        location = str(loc_val).strip()
    elif city_val:
        location = str(city_val).strip()
    else:
        addr = _first_present(raw, ["Address", "address"])
        location = str(addr).strip() if addr else None

    if not name or not location:
        return None

    cuisine_value = _first_present(raw, ["cuisines", "Cuisine", "Cuisines", "dish_liked"])
    cost_value = _first_present(raw, ["cost_for_two", "average_cost_for_two", "Average Cost for two", "approx_cost(for two people)"])
    rating_value = _first_present(raw, ["rating", "aggregate_rating", "Aggregate rating", "rate"])

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
