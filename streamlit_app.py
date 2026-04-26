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

# Hide default chrome + custom widget styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 0 !important; max-width: 100% !important;}
.stApp {background: #ffffff; font-family: 'Poppins', sans-serif;}
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

# ══════════════════════════════════════════════════════════════════════
#  1)  ZOMATO AI SEARCH — AT THE TOP
# ══════════════════════════════════════════════════════════════════════
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
    budget = st.selectbox(
        "💰 Budget", options=["", "low", "medium", "high"], index=0,
        format_func=lambda x: {"": "Any", "low": "Low (≤ ₹800)",
                                "medium": "Medium (≤ ₹2000)", "high": "Premium"}.get(x, x))
with col3:
    cuisine = st.text_input("🍽️ Cuisine", placeholder="e.g. Chinese, Italian")
with col4:
    min_rating = st.slider("⭐ Min Rating", 0.0, 5.0, 3.5, 0.1)

search_clicked = st.button("🔍  Get AI Recommendations")

# ══════════════════════════════════════════════════════════════════════
#  2)  RESULTS — RIGHT BELOW THE SEARCH
# ══════════════════════════════════════════════════════════════════════

# Stock restaurant images to rotate through
FOOD_IMAGES = [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&q=80",
    "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&q=80",
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=80",
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80",
    "https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=400&q=80",
    "https://images.unsplash.com/photo-1544025162-811114bd41cb?w=400&q=80",
    "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=400&q=80",
    "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&q=80",
]

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

        # Build cards — whether LLM returned recs or we fall back to candidates
        display_items = []
        if recs:
            for r in recs:
                rid = r.get("restaurant_id", "")
                cand = cand_map.get(rid)
                display_items.append({
                    "name": cand.name if cand else rid,
                    "cuisines": " • ".join(cand.cuisines[:4]) if cand and cand.cuisines else "—",
                    "cost": f"₹{int(cand.cost_for_two)}" if cand and cand.cost_for_two else "—",
                    "rating": str(cand.rating) if cand and cand.rating else "—",
                    "explanation": r.get("explanation", ""),
                    "rank": r.get("rank", ""),
                    "location": cand.location if cand else "",
                })
        else:
            for idx, c in enumerate(candidates[:8]):
                display_items.append({
                    "name": c.name,
                    "cuisines": " • ".join(c.cuisines[:4]) if c.cuisines else "—",
                    "cost": f"₹{int(c.cost_for_two)}" if c.cost_for_two else "—",
                    "rating": str(c.rating) if c.rating else "—",
                    "explanation": f"{c.name} matches your filters with rating {c.rating}.",
                    "rank": idx + 1,
                    "location": c.location,
                })

        if display_items:
            # Build pure HTML card grid
            cards = ""
            for i, item in enumerate(display_items):
                img = FOOD_IMAGES[i % len(FOOD_IMAGES)]
                cards += f"""
                <div style="background:#fff;border:1px solid #eee;border-radius:16px;overflow:hidden;
                            box-shadow:0 2px 12px rgba(0,0,0,0.06);transition:transform 0.2s;">
                    <img src="{img}" style="width:100%;height:180px;object-fit:cover;">
                    <div style="padding:18px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <div style="font-weight:700;font-size:1.1rem;color:#1c1c1c;">
                                {item['name']}
                            </div>
                            <div style="background:#267E3E;color:#fff;border-radius:8px;padding:3px 8px;
                                        font-weight:700;font-size:0.85rem;">
                                ★ {item['rating']}
                            </div>
                        </div>
                        <div style="font-size:0.82rem;color:#999;margin-bottom:4px;">
                            {item['cuisines']}
                        </div>
                        <div style="font-size:0.82rem;color:#999;margin-bottom:12px;">
                            {item['location']} &nbsp;•&nbsp; {item['cost']} for two
                        </div>
                        <div style="background:#fff5f5;border-radius:10px;padding:12px 14px;font-size:0.85rem;
                                    color:#333;line-height:1.55;">
                            <div style="font-size:0.68rem;font-weight:700;color:#ef4f5f;text-transform:uppercase;
                                        letter-spacing:0.5px;margin-bottom:4px;">AI Reason</div>
                            {item['explanation']}
                        </div>
                    </div>
                </div>
                """

            full_html = f"""
            <!DOCTYPE html><html><head>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
            <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:'Poppins',sans-serif; background:#fafafa; padding:30px 20px; }}
            h2 {{ text-align:center; font-weight:700; font-size:1.7rem; color:#1c1c1c; margin-bottom:6px; }}
            .sub {{ text-align:center; color:#999; font-size:0.88rem; margin-bottom:28px; line-height:1.5; }}
            .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:22px;
                     max-width:1100px; margin:0 auto; }}
            .grid > div:hover {{ transform:translateY(-4px); box-shadow:0 10px 28px rgba(0,0,0,0.10); }}
            </style></head><body>
            <h2>Personalized Picks for You</h2>
            <div class="sub">
                Top recommendations for <b>{cuisine or 'any cuisine'}</b> in <b>{selected_locality}</b>,
                budget <b>{budget or 'any'}</b>, min rating <b>{min_rating}</b>
                &nbsp;·&nbsp; Shortlist {len(candidates)} &nbsp;·&nbsp; LLM ranked
            </div>
            <div class="grid">{cards}</div>
            </body></html>
            """
            row_count = (len(display_items) + 2) // 3
            est_height = 180 + row_count * 520
            components.html(full_html, height=est_height, scrolling=True)


# ══════════════════════════════════════════════════════════════════════
#  3)  HERO SECTION — BELOW THE RESULTS / SEARCH
# ══════════════════════════════════════════════════════════════════════
HERO_HTML = """
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Poppins',sans-serif; background:linear-gradient(135deg,#fff5f5 0%,#ffffff 40%,#fff0f0 100%); overflow-x:hidden; }
.hero { position:relative; width:100%; min-height:820px; display:flex; flex-direction:column;
        align-items:center; justify-content:center; padding:40px 20px; overflow:hidden; }
.hero::before { content:""; position:absolute; width:500px; height:500px;
    border:2px solid rgba(239,79,95,0.12); border-radius:50%;
    top:-120px; left:-100px; animation:drift 18s ease-in-out infinite alternate; }
.hero::after { content:""; position:absolute; width:600px; height:600px;
    border:2px solid rgba(239,79,95,0.10); border-radius:50%;
    bottom:-180px; right:-150px; animation:drift 22s ease-in-out infinite alternate-reverse; }
@keyframes drift { 0%{transform:translate(0,0) rotate(0deg);} 100%{transform:translate(40px,-30px) rotate(15deg);} }
.food { position:absolute; z-index:1; animation:floaty 6s ease-in-out infinite;
        filter:drop-shadow(0 8px 24px rgba(0,0,0,0.10)); }
.food.a { top:18%; left:6%; width:155px; animation-delay:0s; }
.food.b { bottom:22%; right:5%; width:145px; animation-delay:1.5s; }
.food.c { top:4%; right:10%; width:125px; animation-delay:3s; }
.food.d { top:12%; right:22%; width:32px; animation-delay:0.8s; }
.food.e { bottom:38%; left:12%; width:28px; animation-delay:2.2s; }
@keyframes floaty { 0%,100%{transform:translateY(0) rotate(0deg);} 50%{transform:translateY(-18px) rotate(4deg);} }
.title { font-weight:800; font-size:3.2rem; color:#1c1c1c; text-align:center; line-height:1.15; z-index:2; position:relative; }
.title span { color:#ef4f5f; }
.subtitle { font-weight:300; font-size:1.05rem; color:#696969; text-align:center;
            max-width:480px; margin:18px auto 0; line-height:1.7; z-index:2; position:relative; }
.vid-wrap { position:relative; z-index:2; margin-top:40px; border-radius:20px; overflow:hidden;
            box-shadow:0 20px 60px rgba(239,79,95,0.18); width:700px; max-width:90%; }
.vid-wrap video { width:100%; display:block; border-radius:20px; }
.stats { display:flex; justify-content:center; gap:40px; margin-top:45px; z-index:2; position:relative; flex-wrap:wrap; }
.stat { display:flex; align-items:center; gap:12px; background:#fff; border:1px solid #f0f0f0;
        border-radius:14px; padding:16px 24px; box-shadow:0 4px 20px rgba(0,0,0,0.04); }
.stat-n { font-weight:700; font-size:1.4rem; color:#1c1c1c; }
.stat-l { font-size:0.82rem; color:#999; }
.stat-i { font-size:1.6rem; }
</style></head><body>
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
</body></html>
"""

components.html(HERO_HTML, height=880, scrolling=False)
