from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.phases.phase1.settings import Settings
from src.phases.phase2.cleaning import normalize_row
from src.phases.phase2.models import Restaurant
from src.phases.phase2.repository import RestaurantRepository

logger = logging.getLogger(__name__)


def _load_hf_rows(settings: Settings) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency `datasets`. Install with: pip install datasets"
        ) from exc

    logger.info(
        "load_dataset_start name=%s split=%s revision=%s",
        settings.dataset_name,
        settings.dataset_split,
        settings.dataset_revision,
    )
    dataset = load_dataset(
        settings.dataset_name,
        split=settings.dataset_split,
        revision=settings.dataset_revision,
        cache_dir=str(settings.data_cache_dir),
    )
    rows = list(dataset)
    logger.info("load_dataset_done rows=%s", len(rows))
    return rows


def _apply_sample_limit(rows: list[dict[str, Any]], sample_limit: int | None) -> list[dict[str, Any]]:
    if sample_limit is None:
        return rows
    return rows[:sample_limit]


def _normalize_rows(rows: list[dict[str, Any]]) -> list[Restaurant]:
    normalized: list[Restaurant] = []
    for index, row in enumerate(rows):
        result = normalize_row(row, index)
        if result is not None:
            normalized.append(result)
    logger.info(
        "normalize_done input_count=%s output_count=%s dropped=%s",
        len(rows),
        len(normalized),
        len(rows) - len(normalized),
    )
    return normalized


def load_restaurants(settings: Settings) -> RestaurantRepository:
    rows = _load_hf_rows(settings)
    sampled_rows = _apply_sample_limit(rows, settings.sample_limit)
    restaurants = _normalize_rows(sampled_rows)
    return RestaurantRepository(restaurants)


def load_restaurants_from_json(path: Path | str, sample_limit: int | None = None) -> RestaurantRepository:
    file_path = Path(path)
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Fixture JSON must be a list of row objects")
    rows = [row for row in payload if isinstance(row, dict)]
    sampled_rows = _apply_sample_limit(rows, sample_limit)
    restaurants = _normalize_rows(sampled_rows)
    return RestaurantRepository(restaurants)
