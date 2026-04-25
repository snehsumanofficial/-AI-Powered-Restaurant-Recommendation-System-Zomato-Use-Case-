from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Restaurant:
    id: str
    name: str
    location: str
    cuisines: list[str]
    cost_for_two: float | None
    cost_tier: str | None
    rating: float | None
    raw: dict[str, Any]
