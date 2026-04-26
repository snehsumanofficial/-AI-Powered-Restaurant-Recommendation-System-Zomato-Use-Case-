import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
import streamlit.components.v1 as components
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

# Hide default Streamlit chrome + style widgets
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 0 !important; max-width: 100% !important;}
.stApp {background: #ffffff;}
.stSelectbox > div > div { border-radius: 10px !important; }
.stTextInput > div > div > input { border-radius: 10px !important; }
.stButton > button {
    background: #ef4f5f !important; color: white !important; border: none !important;
    border-radius: 10px !important; font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important; font-size: 1.05rem !important;
    padding: 0.6rem 2rem !important; width: 100% !important;
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

# ── HERO SECTION (rendered via components.html to support img/video) ─
HERO_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #fff5f5 0%, #ffffff 40%, #fff0f0 100%); overflow-x: hidden; }

.hero {
    position: relative; width: 100%; min-height: 860px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 40px 20px; overflow: hidden;
}

/* Decorative circles */
.hero::before {
    content: ""; position: absolute; width: 500px; height: 500px;
    border: 2px solid rgba(239,79,95,0.12); border-radius: 50%;
    top: -120px; left: -100px; animation: drift 18s ease-in-out infinite alternate;
}
.hero::after {
    content: ""; position: absolute; width: 600px; height: 600px;
    border: 2px solid rgba(239,79,95,0.10); border-radius: 50%;
    bottom: -180px; right: -150px; animation: drift 22s ease-in-out infinite alternate-reverse;
}
@keyframes drift {
    0%   { transform: translate(0, 0) rotate(0deg); }
    100% { transform: translate(40px, -30px) rotate(15deg); }
}

/* Floating food */
.food { position: absolute; z-index: 1; animation: floaty 6s ease-in-out infinite;
        filter: drop-shadow(0 8px 24px rgba(0,0,0,0.10)); }
.food.a { top: 18%; left: 6%;  width: 155px; animation-delay: 0s; }
.food.b { bottom: 22%; right: 5%; width: 145px; animation-delay: 1.5s; }
.food.c { top: 4%;  right: 10%; width: 125px; animation-delay: 3s; }
.food.d { top: 12%; right: 22%; width: 32px; animation-delay: 0.8s; }
.food.e { bottom: 38%; left: 12%; width: 28px; animation-delay: 2.2s; }
@keyframes floaty {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50%      { transform: translateY(-18px) rotate(4deg); }
}

.title { font-weight: 800; font-size: 3.4rem; color: #1c1c1c; text-align: center;
         line-height: 1.15; z-index: 2; position: relative; }
.title span { color: #ef4f5f; }
.subtitle { font-weight: 300; font-size: 1.1rem; color: #696969; text-align: center;
            max-width: 480px; margin: 18px auto 0; line-height: 1.7; z-index: 2; position: relative; }

.vid-wrap { position: relative; z-index: 2; margin-top: 40px; border-radius: 20px;
            overflow: hidden; box-shadow: 0 20px 60px rgba(239,79,95,0.18);
            width: 700px; max-width: 90%; }
.vid-wrap video { width: 100%; display: block; border-radius: 20px; }

.stats { display: flex; justify-content: center; gap: 40px; margin-top: 45px;
         z-index: 2; position: relative; flex-wrap: wrap; }
.stat { display: flex; align-items: center; gap: 12px; background: #fff;
        border: 1px solid #f0f0f0; border-radius: 14px; padding: 16px 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
.stat-n { font-weight: 700; font-size: 1.4rem; color: #1c1c1c; }
.stat-l { font-size: 0.82rem; color: #999; }
.stat-i { font-size: 1.6rem; }
</style>
</head>
<body>
<div class="hero">
    <img class="food a" src="https://cdn-icons-png.flaticon.com/512/3075/3075977.png">
    <img class="food b" src="https://cdn-icons-png.flaticon.com/512/3595/3595455.png">
    <img class="food c" src="https://cdn-icons-png.flaticon.com/512/1046/1046751.png">
    <img class="food d" src="https://cdn-icons-png.flaticon.com/512/590/590772.png">
    <img class="food e" src="https://cdn-icons-png.flaticon.com/512/590/590772.png">

    <div class="title"><span>Better food</span> for<br>more people</div>
    <div class="subtitle">For over a decade, we've enabled our customers to discover new tastes, delivered right to their doorstep</div>

    <div class="vid-wrap">
        <video autoplay muted loop playsinline>
            <source src="https://b.zmtcdn.com/data/file_assets/5e05c26b91b99ae33bfc1c6d45626cbe1722240498.mp4" type="video/mp4">
        </video>
    </div>

    <div class="stats">
        <div class="stat"><div><div class="stat-n">3,00,000+</div><div class="stat-l">restaurants</div></div><div class="stat-i">🏪</div></div>
        <div class="stat"><div><div class="stat-n">800+</div><div class="stat-l">cities</div></div><div class="stat-i">📍</div></div>
        <div class="stat"><div><div class="stat-n">3 billion+</div><div class="stat-l">orders delivered</div></div><div class="stat-i">📦</div></div>
    </div>
</div>
</body>
</html>
"""

components.html(HERO_HTML, height=920, scrolling=False)

# ── FILTER FORM ──────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 30px 0 10px;">
    <span style="font-family:'Poppins',sans-serif; font-weight:700; font-size:2rem; color:#1c1c1c;">
        Find Your Perfect Meal with <span style="color:#ef4f5f;">Zomato AI</span>
    </span>
    <p style="font-family:'Poppins',sans-serif; color:#999; margin-top:8px;">
        Select your preferences and let our AI recommend the best restaurants for you
    </p>
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
                <div style="background:#fff;border:1px solid #f0f0f0;border-radius:16px;padding:24px;font-family:'Poppins',sans-serif;transition:transform 0.2s;margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <div style="font-weight:700;font-size:1.15rem;color:#1c1c1c;">#{rank}  {name}</div>
                        <div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:4px 10px;font-weight:700;font-size:0.9rem;color:#ef4f5f;">★ {rating}</div>
                    </div>
                    <div style="font-size:0.85rem;color:#999;margin-bottom:14px;">{cuisines_str} &nbsp;•&nbsp; {cost} for two</div>
                    <div style="background:#fff5f5;border-radius:10px;padding:14px 16px;font-size:0.88rem;color:#333;line-height:1.6;">
                        <div style="display:inline-block;font-size:0.7rem;font-weight:700;color:#ef4f5f;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">AI Reason</div>
                        <div>{explanation}</div>
                    </div>
                </div>
                """

            # Render result cards via components.html so they display properly
            result_html = f"""
            <!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
            <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Poppins', sans-serif; background: #fafafa; padding: 30px 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(460px, 1fr)); gap: 20px; max-width: 1100px; margin: 0 auto; }}
            h2 {{ text-align: center; font-weight: 700; font-size: 1.8rem; color: #1c1c1c; margin-bottom: 8px; }}
            .sub {{ text-align: center; color: #999; font-size: 0.9rem; margin-bottom: 30px; }}
            </style></head><body>
            <h2>Personalized Picks for You</h2>
            <div class="sub">Top recommendations for <b>{cuisine or 'any cuisine'}</b> in <b>{selected_locality}</b>,
                budget <b>{budget or 'any'}</b>, min rating <b>{min_rating}</b>
                · Shortlist {len(candidates)} · LLM ranked</div>
            <div class="grid">{cards_html}</div>
            </body></html>
            """
            card_count = len(recs)
            estimated_height = 200 + (card_count * 220)
            components.html(result_html, height=estimated_height, scrolling=True)
        else:
            st.warning("The AI couldn't generate recommendations. Showing raw candidates instead.")
            for c in candidates[:5]:
                st.write(f"**{c.name}** — {', '.join(c.cuisines)} — ★ {c.rating}")
