from __future__ import annotations

import json
from typing import Any

from src.phases.phase1.settings import Settings
from src.phases.phase2.loader import load_restaurants, load_restaurants_from_json
from src.phases.phase2.models import Restaurant
from src.phases.phase3.groq_client import GroqClient
from src.phases.phase3.preferences import UserPreferences


def _matches_preferences(restaurant: Restaurant, prefs: UserPreferences) -> bool:
    if prefs.locality != restaurant.location:
        return False
    if prefs.budget and restaurant.cost_tier and restaurant.cost_tier != prefs.budget:
        return False
    if prefs.min_rating and (restaurant.rating is None or restaurant.rating < prefs.min_rating):
        return False
    if prefs.cuisines and not any(c in restaurant.cuisines for c in prefs.cuisines):
        return False
    return True


def retrieve_candidates(
    prefs: UserPreferences, restaurants: list[Restaurant], top_k: int = 10
) -> list[Restaurant]:
    filtered = [r for r in restaurants if _matches_preferences(r, prefs)]
    filtered.sort(
        key=lambda r: (
            r.rating if r.rating is not None else -1.0,
            -(r.cost_for_two if r.cost_for_two is not None else 0.0),
            r.name,
        ),
        reverse=True,
    )
    return filtered[:top_k]


def build_llm_context(candidates: list[Restaurant], prefs: UserPreferences) -> str:
    payload = {
        "preferences": {
            "locality": prefs.locality,
            "budget": prefs.budget,
            "cuisine": prefs.cuisines,
            "min_rating": prefs.min_rating,
            "extras": prefs.extras,
        },
        "candidates": [
            {
                "id": c.id,
                "name": c.name,
                "location": c.location,
                "cuisines": c.cuisines,
                "rating": c.rating,
                "cost_for_two": c.cost_for_two,
            }
            for c in candidates
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def _fallback_recommendation(candidates: list[Restaurant]) -> dict[str, Any]:
    top = candidates[:5]
    return {
        "summary": "Top restaurants based on structured filters.",
        "recommendations": [
            {
                "restaurant_id": r.id,
                "rank": idx + 1,
                "explanation": (
                    f"{r.name} matches your filters with rating {r.rating} and cuisines "
                    f"{', '.join(r.cuisines) if r.cuisines else 'N/A'}."
                ),
            }
            for idx, r in enumerate(top)
        ],
    }


def recommend_with_groq(
    settings: Settings, prefs: UserPreferences, candidates: list[Restaurant]
) -> dict[str, Any]:
    if not candidates:
        return {"summary": "No restaurants matched your filters.", "recommendations": []}

    # Keep fallback path so app remains usable without key/provider availability.
    if not settings.llm_api_key:
        return _fallback_recommendation(candidates)

    context = build_llm_context(candidates, prefs)
    prompt = (
        "Return strict JSON with keys summary and recommendations. "
        "recommendations must be an array with restaurant_id, rank, explanation. "
        "Use only provided candidate IDs and facts.\n\n"
        f"{context}"
    )
    try:
        client = GroqClient(settings=settings, timeout_seconds=45)
        response = client.chat(prompt, system_prompt="You are a precise restaurant ranking assistant.")
        parsed = json.loads(response.text)
        if isinstance(parsed, dict) and "recommendations" in parsed:
            return parsed
    except Exception:
        pass
    return _fallback_recommendation(candidates)


def load_restaurants_for_app(settings: Settings) -> list[Restaurant]:
    if settings.data_fixture_path:
        repo = load_restaurants_from_json(settings.data_fixture_path, settings.sample_limit)
        return repo.get_all()
    try:
        repo = load_restaurants(settings)
    except Exception:
        repo = load_restaurants_from_json("tests/fixtures/restaurants_sample.json", settings.sample_limit)
    return repo.get_all()


def get_available_localities(restaurants: list[Restaurant]) -> list[str]:
    return sorted({r.location for r in restaurants if r.location})
