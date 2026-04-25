from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FilterSpec:
    locality: str
    budget: str | None
    cuisines: list[str]
    min_rating: float


@dataclass(frozen=True)
class UserPreferences:
    locality: str
    budget: str | None
    cuisines: list[str]
    min_rating: float
    extras: str | None = None

    def to_filter_spec(self) -> FilterSpec:
        return FilterSpec(
            locality=self.locality,
            budget=self.budget,
            cuisines=self.cuisines,
            min_rating=self.min_rating,
        )


_BUDGET_SYNONYMS = {
    "cheap": "low",
    "budget": "low",
    "affordable": "low",
    "moderate": "medium",
    "mid": "medium",
    "expensive": "high",
    "premium": "high",
    "luxury": "high",
}


def _normalize_budget(raw_budget: Any) -> str | None:
    if raw_budget is None:
        return None
    token = str(raw_budget).strip().lower()
    token = _BUDGET_SYNONYMS.get(token, token)
    if token not in {"low", "medium", "high"}:
        raise ValueError("budget must be one of: low, medium, high")
    return token


def _normalize_cuisines(raw_cuisine: Any) -> list[str]:
    if raw_cuisine is None:
        return []
    if isinstance(raw_cuisine, str):
        parts = [x.strip().lower() for x in raw_cuisine.split(",") if x.strip()]
    elif isinstance(raw_cuisine, list):
        parts = [str(x).strip().lower() for x in raw_cuisine if str(x).strip()]
    else:
        raise ValueError("cuisine must be a string or list of strings")
    return sorted(set(parts))


def parse_preferences(raw: dict[str, Any]) -> UserPreferences:
    locality_raw = raw.get("locality", raw.get("location", ""))
    locality = str(locality_raw).strip().lower()
    if not locality:
        raise ValueError("locality is required")

    budget = _normalize_budget(raw.get("budget"))
    cuisines = _normalize_cuisines(raw.get("cuisine"))

    min_rating_raw = raw.get("min_rating", 0.0)
    try:
        min_rating = float(min_rating_raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("min_rating must be a number") from exc
    if min_rating < 0 or min_rating > 5:
        raise ValueError("min_rating must be between 0 and 5")

    extras_value = raw.get("extras")
    extras = str(extras_value).strip() if extras_value is not None else None
    if extras == "":
        extras = None

    return UserPreferences(
        locality=locality,
        budget=budget,
        cuisines=cuisines,
        min_rating=min_rating,
        extras=extras,
    )
