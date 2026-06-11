from __future__ import annotations

import json
import logging
import re
from typing import Any

log = logging.getLogger(__name__)

from src.phases.phase1.settings import Settings
from src.phases.phase2.loader import load_restaurants, load_restaurants_from_json
from src.phases.phase2.models import Restaurant
from src.phases.phase3.groq_client import GroqClient
from src.phases.phase3.preferences import UserPreferences


_BUDGET_LEVELS = {"low": 1, "medium": 2, "high": 3}

def _locality_matches(restaurant_loc: str, pref_loc: str) -> bool:
    """Check if locality matches using substring in either direction."""
    rl = restaurant_loc.lower()
    pl = pref_loc.lower()
    if rl == pl:
        return True
    if pl in rl or rl in pl:
        return True
    # Match on first word (e.g. 'banashankari' matches 'banashankari, bangalore')
    pl_first = pl.split(",")[0].strip()
    rl_first = rl.split(",")[0].strip()
    if pl_first and rl_first and (pl_first in rl_first or rl_first in pl_first):
        return True
    return False


def _matches_preferences(restaurant: Restaurant, prefs: UserPreferences,
                         relax_cuisine: bool = False, relax_rating: bool = False) -> bool:
    # Locality is always required
    if prefs.locality and not _locality_matches(restaurant.location, prefs.locality):
        return False

    if prefs.budget and restaurant.cost_tier:
        pref_level = _BUDGET_LEVELS.get(prefs.budget, 3)
        rest_level = _BUDGET_LEVELS.get(restaurant.cost_tier, 3)
        if rest_level > pref_level:
            return False

    if not relax_rating:
        if prefs.min_rating and (restaurant.rating is None or restaurant.rating < prefs.min_rating):
            return False

    if prefs.cuisines and not relax_cuisine:
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
    prefs: UserPreferences, restaurants: list[Restaurant], top_k: int = 30
) -> list[Restaurant]:
    """Progressive retrieval: strict first, then relax filters if too few results."""
    # Pass 1: strict match
    filtered = [r for r in restaurants if _matches_preferences(r, prefs)]
    log.info("Pass 1 (strict): %d candidates", len(filtered))

    # Pass 2: relax cuisine if too few
    if len(filtered) < 5 and prefs.cuisines:
        filtered = [r for r in restaurants if _matches_preferences(r, prefs, relax_cuisine=True)]
        log.info("Pass 2 (relax cuisine): %d candidates", len(filtered))

    # Pass 3: relax rating if still too few
    if len(filtered) < 5:
        filtered = [r for r in restaurants if _matches_preferences(r, prefs, relax_cuisine=True, relax_rating=True)]
        log.info("Pass 3 (relax all): %d candidates", len(filtered))

    # Deduplicate by name (some datasets have duplicates)
    seen_names: set[str] = set()
    unique: list[Restaurant] = []
    for r in filtered:
        key = r.name.lower().strip()
        if key not in seen_names:
            seen_names.add(key)
            unique.append(r)
    filtered = unique

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
    top = candidates[:10]
    return {
        "summary": f"Found {len(candidates)} restaurants matching your filters. Here are the top {len(top)} picks sorted by rating.",
        "recommendations": [
            {
                "restaurant_id": r.id,
                "rank": idx + 1,
                "explanation": (
                    f"{r.name} is a great choice with a rating of {r.rating}/5"
                    f"{' serving ' + ', '.join(r.cuisines[:3]) if r.cuisines else ''}"
                    f"{' at ₹' + str(int(r.cost_for_two)) + ' for two' if r.cost_for_two else ''}"
                    f" in {r.location}."
                ),
            }
            for idx, r in enumerate(top)
        ],
    }


def _extract_json(text: str) -> dict[str, Any] | None:
    """Extract JSON from LLM response, handling markdown code fences."""
    # Strip markdown code fences like ```json ... ```
    cleaned = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r'```\s*$', '', cleaned.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Try to find JSON object in the text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def recommend_with_groq(
    settings: Settings, prefs: UserPreferences, candidates: list[Restaurant]
) -> dict[str, Any]:
    if not candidates:
        return {"summary": "No restaurants matched your filters.", "recommendations": []}

    # Keep fallback path so app remains usable without key/provider availability.
    if not settings.llm_api_key:
        log.info("No LLM_API_KEY set — using fallback recommendations.")
        return _fallback_recommendation(candidates)

    context = build_llm_context(candidates, prefs)
    prompt = (
        f"USER PREFERENCES:\n- Cuisines: {', '.join(prefs.cuisines) if prefs.cuisines else 'Any'}\n"
        f"- Min Rating: {prefs.min_rating}\n- Locality: {prefs.locality}\n\n"
        "CANDIDATE RESTAURANTS:\n"
        f"{context}\n\n"
        "TASK: Rank the top 8 restaurants that BEST match the user's cuisine and rating preferences. "
        "Return ONLY raw JSON (no markdown, no code fences) with keys 'summary' and 'recommendations'. "
        "In 'summary', explain exactly how these choices fit the requested cuisine and rating. "
        "In 'recommendations', provide an array of 8 objects with 'restaurant_id', 'rank', and 'explanation'. "
        "Include ALL 8 different restaurants — variety is important. "
        "The 'explanation' must mention why the cuisine and rating are a good match."
    )
    try:
        client = GroqClient(settings=settings, timeout_seconds=45)
        response = client.chat(
            prompt,
            system_prompt="You are a precise Zomato restaurant recommender. Always return raw JSON only — no markdown, no code fences. Always prioritize the user's specific cuisine and rating filters."
        )
        log.info("Groq raw response (first 500 chars): %s", response.text[:500])
        parsed = _extract_json(response.text)
        if isinstance(parsed, dict) and "recommendations" in parsed:
            return parsed
        log.warning("Groq response did not contain 'recommendations' key. Parsed: %s", type(parsed))
    except Exception as exc:
        log.error("Groq LLM call failed: %s", exc, exc_info=True)
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
