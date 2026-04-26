from __future__ import annotations

import json
from typing import Any

from src.phases.phase1.settings import Settings
from src.phases.phase2.loader import load_restaurants, load_restaurants_from_json
from src.phases.phase2.models import Restaurant
from src.phases.phase3.groq_client import GroqClient
from src.phases.phase3.preferences import UserPreferences


_BUDGET_LEVELS = {"low": 1, "medium": 2, "high": 3}

def _matches_preferences(restaurant: Restaurant, prefs: UserPreferences) -> bool:
    if prefs.locality and prefs.locality.lower() != restaurant.location.lower():
        if prefs.locality.lower() not in restaurant.location.lower() and restaurant.location.lower() not in prefs.locality.lower():
            return False
            
    if prefs.budget and restaurant.cost_tier:
        pref_level = _BUDGET_LEVELS.get(prefs.budget, 3)
        rest_level = _BUDGET_LEVELS.get(restaurant.cost_tier, 3)
        if rest_level > pref_level:
            return False
            
    if prefs.min_rating and (restaurant.rating is None or restaurant.rating < prefs.min_rating):
        return False
        
    if prefs.cuisines:
        restaurant_cuisines_lower = [c.lower() for c in restaurant.cuisines]
        matched = False
        for pref_c in prefs.cuisines:
            pref_c_lower = pref_c.lower()
            if any(pref_c_lower in rc for rc in restaurant_cuisines_lower):
                matched = True
                break
        if not matched:
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
        "summary": f"Found {len(candidates)} restaurants matching your filters. Here are the top picks sorted by rating.",
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
        f"USER PREFERENCES:\n- Cuisines: {', '.join(prefs.cuisines) if prefs.cuisines else 'Any'}\n"
        f"- Min Rating: {prefs.min_rating}\n- Locality: {prefs.locality}\n\n"
        "CANDIDATE RESTAURANTS:\n"
        f"{context}\n\n"
        "TASK: Rank the top 5 restaurants that BEST match the user's cuisine and rating preferences. "
        "Return strict JSON with keys 'summary' and 'recommendations'. "
        "In 'summary', explain exactly how these choices fit the requested cuisine and rating. "
        "In 'recommendations', provide an array of objects with 'restaurant_id', 'rank', and 'explanation'. "
        "The 'explanation' must mention why the cuisine and rating are a good match."
    )
    try:
        client = GroqClient(settings=settings, timeout_seconds=45)
        response = client.chat(prompt, system_prompt="You are a precise Zomato restaurant recommender. Always prioritize the user's specific cuisine and rating filters.")
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
