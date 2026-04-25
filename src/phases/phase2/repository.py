from __future__ import annotations

from collections.abc import Callable, Iterable

from src.phases.phase2.models import Restaurant


class RestaurantRepository:
    def __init__(self, restaurants: list[Restaurant]) -> None:
        self._restaurants = restaurants

    def get_all(self) -> list[Restaurant]:
        return list(self._restaurants)

    def query(
        self, predicate: Callable[[Restaurant], bool]
    ) -> Iterable[Restaurant]:
        return (restaurant for restaurant in self._restaurants if predicate(restaurant))
