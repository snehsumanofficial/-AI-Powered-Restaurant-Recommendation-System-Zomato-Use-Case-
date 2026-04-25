from src.phases.phase2.cleaning import derive_cost_tier, normalize_row, parse_cuisines


def test_parse_cuisines_normalizes_and_deduplicates() -> None:
    cuisines = parse_cuisines("Chinese,  Thai,Chinese")
    assert cuisines == ["chinese", "thai"]


def test_cost_tier_mapping() -> None:
    assert derive_cost_tier(400) == "low"
    assert derive_cost_tier(1200) == "medium"
    assert derive_cost_tier(2200) == "high"
    assert derive_cost_tier(None) is None


def test_normalize_row_handles_nulls_and_clamps_rating() -> None:
    raw = {
        "Restaurant Name": "Test Place",
        "Locality": "Delhi",
        "Cuisines": None,
        "Average Cost for two": "1500",
        "Aggregate rating": "9.5",
    }
    restaurant = normalize_row(raw, row_index=7)
    assert restaurant is not None
    assert restaurant.name == "Test Place"
    assert restaurant.location == "delhi"
    assert restaurant.cuisines == []
    assert restaurant.cost_for_two == 1500.0
    assert restaurant.cost_tier == "medium"
    assert restaurant.rating == 5.0
