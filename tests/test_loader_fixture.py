from pathlib import Path

from src.phases.phase2.loader import load_restaurants_from_json


def test_fixture_loading_and_normalization() -> None:
    fixture_path = Path("tests/fixtures/restaurants_sample.json")
    repo = load_restaurants_from_json(fixture_path)
    restaurants = repo.get_all()

    # One invalid row with missing name should be dropped.
    assert len(restaurants) == 3

    assert restaurants[0].name == "Spice Garden"
    assert restaurants[0].cuisines == ["chinese", "north indian"]
    assert restaurants[0].cost_tier == "low"
    assert restaurants[1].cost_tier == "medium"
    assert restaurants[2].cost_tier == "high"


def test_fixture_respects_sample_limit() -> None:
    fixture_path = Path("tests/fixtures/restaurants_sample.json")
    repo = load_restaurants_from_json(fixture_path, sample_limit=2)
    assert len(repo.get_all()) == 2
