import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
from src.phases.phase1.settings import load_settings
from src.phases.phase3.preferences import UserPreferences
from src.phases.phase3.service import (
    load_restaurants_for_app,
    get_available_localities,
    retrieve_candidates,
    recommend_with_groq
)

st.set_page_config(page_title="Zomato AI Backend (Streamlit)", layout="wide")
st.title("Zomato AI Recommendation - Backend API Testing Interface")

# Initialize backend data
@st.cache_resource
def init_system():
    settings = load_settings()
    restaurants = load_restaurants_for_app(settings)
    localities = get_available_localities(restaurants)
    return settings, restaurants, localities

settings, restaurants, localities = init_system()

st.sidebar.header("Test API Filters")
selected_locality = st.sidebar.selectbox("Locality", options=localities)
budget = st.sidebar.selectbox("Budget", options=["", "low", "medium", "high"])
cuisine = st.sidebar.text_input("Cuisine (e.g. North Indian)")
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.5, 0.1)

if st.sidebar.button("Run Backend Logic"):
    prefs = UserPreferences(
        locality=selected_locality,
        budget=budget if budget else None,
        cuisines=[c.strip() for c in cuisine.split(",") if c.strip()],
        min_rating=min_rating,
    )
    
    with st.spinner("Retrieving candidates using Pydantic validation..."):
        candidates = retrieve_candidates(prefs, restaurants, top_k=15)
        st.success(f"Backend retrieved {len(candidates)} candidate matches.")
        
    with st.spinner("Running Groq LLM inference..."):
        result = recommend_with_groq(settings, prefs, candidates)
        
    st.subheader("LLM Response:")
    st.write(result.get("summary", "Results"))
    
    recs = result.get("recommendations", [])
    if not recs:
        st.warning("No recommendations generated from LLM.")
    else:
        for r in recs:
            # We match to candidates to get the real name
            name = next((c.name for c in candidates if c.id == r.get("restaurant_id")), r.get("restaurant_id"))
            st.markdown(f"**Rank {r.get('rank')}: {name}**")
            st.info(r.get('explanation'))
