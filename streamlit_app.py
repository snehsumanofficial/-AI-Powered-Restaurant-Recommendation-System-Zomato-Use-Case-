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

st.set_page_config(
    page_title="Zomato AI — Restaurant Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inject Premium CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* Hide default Streamlit chrome */
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important;}
.stApp {background: #ffffff;}

/* ── HERO ─────────────────────────────────────────── */
.hero-section {
    position: relative;
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    min-height: 92vh;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 40%, #fff0f0 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* animated curvy accent lines */
.hero-section::before {
    content: "";
    position: absolute;
    width: 500px; height: 500px;
    border: 2px solid rgba(239,79,95,0.12);
    border-radius: 50%;
    top: -120px; left: -100px;
    animation: drift 18s ease-in-out infinite alternate;
}
.hero-section::after {
    content: "";
    position: absolute;
    width: 600px; height: 600px;
    border: 2px solid rgba(239,79,95,0.10);
    border-radius: 50%;
    bottom: -180px; right: -150px;
    animation: drift 22s ease-in-out infinite alternate-reverse;
}
@keyframes drift {
    0%   { transform: translate(0, 0) rotate(0deg); }
    100% { transform: translate(40px, -30px) rotate(15deg); }
}

/* floating food items */
.food-float {
    position: absolute;
    animation: floaty 6s ease-in-out infinite;
    z-index: 1;
    filter: drop-shadow(0 8px 24px rgba(0,0,0,0.10));
}
.food-float.burger   { top: 22%; left: 8%;  width: 160px; animation-delay: 0s; }
.food-float.pizza    { bottom: 18%; right: 6%; width: 150px; animation-delay: 1.5s; }
.food-float.dumpling { top: 6%;  right: 12%; width: 130px; animation-delay: 3s; }
.food-float.chili1   { top: 15%; right: 25%; width: 35px; animation-delay: 0.8s; }
.food-float.chili2   { bottom: 35%; left: 15%; width: 30px; animation-delay: 2.2s; }

@keyframes floaty {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50%      { transform: translateY(-18px) rotate(4deg); }
}

.hero-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 3.6rem;
    color: #1c1c1c;
    text-align: center;
    line-height: 1.15;
    z-index: 2;
    position: relative;
}
.hero-title span { color: #ef4f5f; }
.hero-subtitle {
    font-family: 'Poppins', sans-serif;
    font-weight: 300;
    font-size: 1.15rem;
    color: #696969;
    text-align: center;
    max-width: 480px;
    margin-top: 18px;
    line-height: 1.7;
    z-index: 2;
    position: relative;
}

/* video embed container */
.video-wrapper {
    position: relative;
    z-index: 2;
    margin-top: 40px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(239,79,95,0.18);
    width: 720px;
    max-width: 90vw;
}
.video-wrapper video {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 20px;
}

/* ── STATS BAR ────────────────────────────────────── */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 50px;
    margin-top: 50px;
    z-index: 2;
    position: relative;
    flex-wrap: wrap;
}
.stat-item {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #ffffff;
    border: 1px solid #f0f0f0;
    border-radius: 14px;
    padding: 18px 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
}
.stat-num {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: #1c1c1c;
}
.stat-label {
    font-family: 'Poppins', sans-serif;
    font-size: 0.85rem;
    color: #999;
}
.stat-icon { font-size: 1.8rem; }

/* ── FILTER FORM SECTION ──────────────────────────── */
.form-section {
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    background: #fafafa;
    padding: 60px 20px;
}
.form-inner {
    max-width: 900px;
    margin: 0 auto;
}
.section-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    color: #1c1c1c;
    text-align: center;
    margin-bottom: 8px;
}
.section-sub {
    font-family: 'Poppins', sans-serif;
    font-weight: 300;
    color: #999;
    text-align: center;
    margin-bottom: 35px;
}

/* ── RESULT CARDS ─────────────────────────────────── */
.results-section {
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    padding: 60px 20px;
    background: #ffffff;
}
.results-inner { max-width: 1100px; margin: 0 auto; }

.rec-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
    gap: 24px;
    margin-top: 30px;
}
.rec-card {
    background: #ffffff;
    border: 1px solid #f0f0f0;
    border-radius: 16px;
    padding: 24px;
    transition: transform 0.2s, box-shadow 0.2s;
    font-family: 'Poppins', sans-serif;
}
.rec-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.08);
}
.rec-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.rec-name { font-weight: 700; font-size: 1.15rem; color: #1c1c1c; }
.rec-rating {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 0.9rem;
    color: #ef4f5f;
}
.rec-meta { font-size: 0.85rem; color: #999; margin-bottom: 14px; }
.rec-reason {
    background: #fff5f5;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 0.88rem;
    color: #333;
    line-height: 1.6;
}
.rec-reason-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    color: #ef4f5f;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

/* Streamlit widget overrides */
.stSelectbox > div > div { border-radius: 10px !important; }
.stTextInput > div > div > input { border-radius: 10px !important; }
.stButton > button {
    background: #ef4f5f !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #d64550 !important;
    box-shadow: 0 6px 20px rgba(239,79,95,0.25) !important;
}
</style>
""", unsafe_allow_html=True)


# ── DATA INIT ────────────────────────────────────────────────────────
@st.cache_resource
def init_system():
    settings = load_settings()
    restaurants = load_restaurants_for_app(settings)
    localities = get_available_localities(restaurants)
    return settings, restaurants, localities

settings, restaurants, localities = init_system()


# ── HERO SECTION ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">

    <img class="food-float burger"
         src="https://cdn-icons-png.flaticon.com/512/3075/3075977.png" alt="">
    <img class="food-float pizza"
         src="https://cdn-icons-png.flaticon.com/512/3595/3595455.png" alt="">
    <img class="food-float dumpling"
         src="https://cdn-icons-png.flaticon.com/512/1046/1046751.png" alt="">
    <img class="food-float chili1"
         src="https://cdn-icons-png.flaticon.com/512/590/590772.png" alt="">
    <img class="food-float chili2"
         src="https://cdn-icons-png.flaticon.com/512/590/590772.png" alt="">

    <div class="hero-title">
        <span>Better food</span> for<br>more people
    </div>
    <div class="hero-subtitle">
        For over a decade, we've enabled our customers to discover new tastes,
        delivered right to their doorstep
    </div>

    <div class="video-wrapper">
        <video autoplay muted loop playsinline>
            <source src="https://b.zmtcdn.com/data/file_assets/5e05c26b91b99ae33bfc1c6d45626cbe1722240498.mp4" type="video/mp4">
        </video>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <div>
                <div class="stat-num">3,00,000+</div>
                <div class="stat-label">restaurants</div>
            </div>
            <div class="stat-icon">🏪</div>
        </div>
        <div class="stat-item">
            <div>
                <div class="stat-num">800+</div>
                <div class="stat-label">cities</div>
            </div>
            <div class="stat-icon">📍</div>
        </div>
        <div class="stat-item">
            <div>
                <div class="stat-num">3 billion+</div>
                <div class="stat-label">orders delivered</div>
            </div>
            <div class="stat-icon">📦</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── FILTER FORM ──────────────────────────────────────────────────────
st.markdown("""
<div class="form-section">
    <div class="form-inner">
        <div class="section-title">Find Your Perfect Meal with <span style="color:#ef4f5f">Zomato AI</span></div>
        <div class="section-sub">Select your preferences and let our AI recommend the best restaurants for you</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_locality = st.selectbox("📍 Locality", options=localities, index=0)
with col2:
    budget = st.selectbox("💰 Budget", options=["", "low", "medium", "high"], index=0,
                          format_func=lambda x: {"": "Any", "low": "Low (≤ ₹800)", "medium": "Medium (≤ ₹2000)", "high": "Premium"}.get(x, x))
with col3:
    cuisine = st.text_input("🍽️ Cuisine", placeholder="e.g. Chinese, Italian")
with col4:
    min_rating = st.slider("⭐ Min Rating", 0.0, 5.0, 3.5, 0.1)

search_clicked = st.button("🔍  Get AI Recommendations")


# ── RESULTS ──────────────────────────────────────────────────────────
if search_clicked:
    prefs = UserPreferences(
        locality=selected_locality,
        budget=budget if budget else None,
        cuisines=[c.strip() for c in cuisine.split(",") if c.strip()],
        min_rating=min_rating,
    )

    with st.spinner("🔎 Finding the best restaurants for you…"):
        candidates = retrieve_candidates(prefs, restaurants, top_k=15)

    if not candidates:
        st.warning("No restaurants matched those filters. Try relaxing your criteria.")
    else:
        with st.spinner("🤖 Asking our AI to rank and explain…"):
            result = recommend_with_groq(settings, prefs, candidates)

        summary = result.get("summary", "")
        recs = result.get("recommendations", [])

        # Build a lookup from candidate id → Restaurant object
        cand_map = {c.id: c for c in candidates}

        if summary:
            st.success(summary)

        if recs:
            cards_html = ""
            for r in recs:
                rid = r.get("restaurant_id", "")
                cand = cand_map.get(rid)
                name = cand.name if cand else rid
                cuisines_str = " • ".join(cand.cuisines[:4]) if cand and cand.cuisines else "—"
                cost = f"₹{int(cand.cost_for_two)}" if cand and cand.cost_for_two else "—"
                rating = cand.rating if cand and cand.rating else "—"
                explanation = r.get("explanation", "")
                rank = r.get("rank", "")

                cards_html += f"""
                <div class="rec-card">
                    <div class="rec-header">
                        <div class="rec-name">#{rank}  {name}</div>
                        <div class="rec-rating">★ {rating}</div>
                    </div>
                    <div class="rec-meta">{cuisines_str} &nbsp;•&nbsp; {cost} for two</div>
                    <div class="rec-reason">
                        <div class="rec-reason-badge">AI Reason</div>
                        <div>{explanation}</div>
                    </div>
                </div>
                """

            st.markdown(f"""
            <div class="results-section">
                <div class="results-inner">
                    <div class="section-title">Personalized Picks for You</div>
                    <div class="section-sub">
                        Top recommendations for <b>{cuisine or 'any cuisine'}</b> in <b>{selected_locality}</b>,
                        budget <b>{budget or 'any'}</b>, min rating <b>{min_rating}</b>
                        &nbsp;·&nbsp; Shortlist {len(candidates)} &nbsp;·&nbsp; LLM ranked
                    </div>
                    <div class="rec-grid">
                        {cards_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("The AI couldn't generate recommendations. Showing raw candidates instead.")
            for c in candidates[:5]:
                st.write(f"**{c.name}** — {', '.join(c.cuisines)} — ★ {c.rating}")
