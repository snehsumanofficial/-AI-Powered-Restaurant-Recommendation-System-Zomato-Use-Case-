from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.phases.phase1.settings import load_settings
from src.phases.phase3.preferences import parse_preferences
from src.phases.phase3.service import (
    get_available_localities,
    load_restaurants_for_app,
    recommend_with_groq,
    retrieve_candidates,
)


class RecommendRequest(BaseModel):
    locality: str
    budget: str | None = None
    cuisine: str | list[str] | None = None
    min_rating: float = 0.0
    extras: str | None = None


app = FastAPI(title="Restaurant Recommender API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_SETTINGS = load_settings()
_RESTAURANTS = load_restaurants_for_app(_SETTINGS)
_LOCALITIES = get_available_localities(_RESTAURANTS)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "loaded_restaurants": len(_RESTAURANTS),
        "llm_model": _SETTINGS.llm_model,
        "llm_key_present": bool(_SETTINGS.llm_api_key),
    }


@app.post("/recommend")
def recommend(request: RecommendRequest) -> dict[str, Any]:
    try:
        prefs = parse_preferences(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    candidates = retrieve_candidates(prefs, _RESTAURANTS, top_k=15)
    llm_result = recommend_with_groq(_SETTINGS, prefs, candidates)
    id_to_restaurant = {r.id: r for r in candidates}

    enriched = []
    for rec in llm_result.get("recommendations", []):
        restaurant = id_to_restaurant.get(rec.get("restaurant_id", ""))
        if restaurant is None:
            continue
        enriched.append(
            {
                "rank": rec.get("rank"),
                "restaurant_id": restaurant.id,
                "name": restaurant.name,
                "locality": restaurant.location,
                "cuisines": restaurant.cuisines,
                "rating": restaurant.rating,
                "cost_for_two": restaurant.cost_for_two,
                "cost_tier": restaurant.cost_tier,
                "explanation": rec.get("explanation"),
            }
        )

    return {
        "summary": llm_result.get("summary", ""),
        "count": len(enriched),
        "recommendations": enriched,
    }


@app.get("/localities")
def localities() -> dict[str, Any]:
    return {
        "count": len(_LOCALITIES),
        "localities": _LOCALITIES,
    }
