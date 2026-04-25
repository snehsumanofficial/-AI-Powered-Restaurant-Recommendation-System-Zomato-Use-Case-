import pytest

from src.phases.phase3.preferences import parse_preferences


def test_parse_preferences_happy_path() -> None:
    prefs = parse_preferences(
        {
            "locality": "Delhi",
            "budget": "cheap",
            "cuisine": "Chinese, Thai",
            "min_rating": 4.1,
        }
    )
    assert prefs.locality == "delhi"
    assert prefs.budget == "low"
    assert prefs.cuisines == ["chinese", "thai"]
    assert prefs.min_rating == 4.1


def test_parse_preferences_rejects_missing_location() -> None:
    with pytest.raises(ValueError, match="locality is required"):
        parse_preferences({"locality": " ", "budget": "low"})
