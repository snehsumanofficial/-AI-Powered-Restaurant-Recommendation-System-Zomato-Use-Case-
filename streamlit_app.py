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


# Hide default chrome + custom widget styles + Floating Food Items
ST_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 0 !important; max-width: 100% !important;}
.stApp {
    background: linear-gradient(160deg, rgba(255,214,224,0.7) 0%, rgba(255,175,197,0.7) 100%) !important;
    font-family: 'Poppins', sans-serif;
    overflow-x: hidden !important;
}

/* Background Video Styling */
#bg-video {
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    z-index: -1;
    object-fit: cover;
    opacity: 0.45;
}
.stSelectbox > div > div { border-radius: 10px !important; background: rgba(255,255,255,0.9) !important; font-size: 1.1rem !important; }
.stTextInput > div > div > input { border-radius: 10px !important; background: rgba(255,255,255,0.9) !important; font-size: 1.1rem !important; }

/* Label Styling */
div[data-testid="stWidgetLabel"] p {
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: #1c1c1c !important;
    letter-spacing: -0.5px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ef4f5f, #e8364a) !important; color: white !important; border: none !important;
    border-radius: 12px !important; font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important; font-size: 1.2rem !important;
    padding: 0.8rem 2rem !important; width: 100% !important;
    box-shadow: 0 4px 15px rgba(239,79,95,0.3) !important;
    margin-top: 10px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #d64550, #c42f3e) !important;
    box-shadow: 0 8px 25px rgba(239,79,95,0.4) !important;
    transform: translateY(-1px);
}

/* Floating Food Animations */
@keyframes floatAcross {
    0%   { transform: translateX(-20vw) translateY(0) rotate(-10deg); }
    50%  { transform: translateX(50vw) translateY(-40px) rotate(15deg); }
    100% { transform: translateX(120vw) translateY(20px) rotate(-15deg); }
}

.floating-food {
    position: fixed;
    z-index: 0;
    pointer-events: none;
    animation: floatAcross linear infinite;
    display: flex;
    flex-direction: column;
    align-items: center;
    opacity: 0.9;
}

.floating-food .emoji {
    font-size: 90px;
    filter: drop-shadow(0 15px 25px rgba(239,79,95,0.3));
    position: relative;
}

.floating-food .face {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -40%);
    font-size: 22px;
    font-weight: 800;
    color: #444;
    text-shadow: 0 2px 4px rgba(255,255,255,0.9);
}

.floating-food .speech {
    background: #fff;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ef4f5f;
    margin-bottom: 5px;
    box-shadow: 0 4px 15px rgba(239,79,95,0.2);
    font-family: 'Poppins', sans-serif;
}
</style>

<!-- Full Page Background Video -->
<video autoplay muted loop playsinline id="bg-video" style="position:fixed; top:0; left:0; width:100vw; height:100vh; object-fit:cover; z-index:-1; opacity:0.5;">
    <source src="https://b.zmtcdn.com/data/file_assets/5e05c26b91b99ae33bfc1c6d45626cbe1722240498.mp4" type="video/mp4">
</video>

<!-- 10 Floating Kawaii Food Characters -->
<div class="floating-food" style="top: 15%; animation-duration: 25s; animation-delay: 0s;">
    <div class="speech">Hi! 😊</div>
    <div class="emoji">🍔<div class="face">◕‿◕</div></div>
</div>
<div class="floating-food" style="top: 40%; animation-duration: 35s; animation-delay: -5s;">
    <div class="speech">Yum! 🥰</div>
    <div class="emoji">🍕<div class="face">^ω^</div></div>
</div>
<div class="floating-food" style="top: 65%; animation-duration: 28s; animation-delay: -10s;">
    <div class="speech">Hey! ✨</div>
    <div class="emoji">🍩<div class="face">°o°</div></div>
</div>
<div class="floating-food" style="top: 85%; animation-duration: 40s; animation-delay: -15s;">
    <div class="speech">Hola! 🌮</div>
    <div class="emoji">🌮<div class="face">♥‿♥</div></div>
</div>
<div class="floating-food" style="top: 10%; animation-duration: 32s; animation-delay: -20s;">
    <div class="speech">Hello!</div>
    <div class="emoji">🍣<div class="face">☆ω☆</div></div>
</div>
<div class="floating-food" style="top: 30%; animation-duration: 38s; animation-delay: -25s;">
    <div class="speech">Sweet!</div>
    <div class="emoji">🍰<div class="face">˘▾˘</div></div>
</div>
<div class="floating-food" style="top: 55%; animation-duration: 22s; animation-delay: -8s;">
    <div class="speech">Heyyy 😄</div>
    <div class="emoji">🧁<div class="face">⊙ω⊙</div></div>
</div>
<div class="floating-food" style="top: 75%; animation-duration: 30s; animation-delay: -18s;">
    <div class="speech">Namaste!</div>
    <div class="emoji">🍜<div class="face">ᵔᴥᵔ</div></div>
</div>
<div class="floating-food" style="top: 20%; animation-duration: 45s; animation-delay: -2s;">
    <div class="speech">Cool! 🍦</div>
    <div class="emoji">🍦<div class="face">≧◡≦</div></div>
</div>
<div class="floating-food" style="top: 80%; animation-duration: 26s; animation-delay: -12s;">
    <div class="speech">Bonjour!</div>
    <div class="emoji">🥐<div class="face">•̀ᴗ•́</div></div>
</div>
"""
st.markdown(ST_STYLE, unsafe_allow_html=True)

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
<div style="text-align:center; padding: 40px 0 20px; z-index: 10; position: relative;">
    <h1 style="font-family:'Poppins',sans-serif; font-weight:800; font-size:3.5rem; color:#1c1c1c; margin:0; line-height:1.2;">
        Find Your Perfect Meal with <span style="color:#ef4f5f;">Zomato AI</span>
    </h1>
    <p style="font-family:'Poppins',sans-serif; color:#444; font-size:1.3rem; margin-top:12px; font-weight:400;">
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

if not search_clicked:
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; margin-top:50px; z-index:10; position:relative;">
        <div style="font-weight:800; font-size:3.6rem; color:#1c1c1c; text-align:center; line-height:1.15; font-family:'Poppins',sans-serif;">
            <span style="color:#ef4f5f;">Better food</span> for<br>more people
        </div>
        <div style="font-weight:300; font-size:1.2rem; color:#444; text-align:center; max-width:550px; margin:20px auto 0; line-height:1.7; font-family:'Poppins',sans-serif;">
            For over a decade, we've enabled our customers to discover new tastes, delivered right to their doorstep
        </div>
        <div style="margin-top:40px; border-radius:20px; overflow:hidden; box-shadow:0 20px 60px rgba(239,79,95,0.28); width:720px; max-width:90%; border:3px solid rgba(239,79,95,0.2);">
            <video autoplay muted loop playsinline style="width:100%; display:block; border-radius:18px;">
                <source src="https://b.zmtcdn.com/data/file_assets/5e05c26b91b99ae33bfc1c6d45626cbe1722240498.mp4" type="video/mp4">
            </video>
        </div>
        <div style="display:flex; justify-content:center; gap:40px; margin-top:50px; flex-wrap:wrap; font-family:'Poppins',sans-serif;">
            <div style="display:flex; align-items:center; gap:12px; background:rgba(255,255,255,0.9); backdrop-filter:blur(10px); border:1px solid rgba(239,79,95,0.15); border-radius:16px; padding:18px 26px; box-shadow:0 4px 20px rgba(239,79,95,0.12);">
                <div><div style="font-weight:800; font-size:1.5rem; color:#1c1c1c;">3,00,000+</div><div style="font-size:0.9rem; color:#999; font-weight:500;">restaurants</div></div><div style="font-size:2rem;">🏪</div>
            </div>
            <div style="display:flex; align-items:center; gap:12px; background:rgba(255,255,255,0.9); backdrop-filter:blur(10px); border:1px solid rgba(239,79,95,0.15); border-radius:16px; padding:18px 26px; box-shadow:0 4px 20px rgba(239,79,95,0.12);">
                <div><div style="font-weight:800; font-size:1.5rem; color:#1c1c1c;">800+</div><div style="font-size:0.9rem; color:#999; font-weight:500;">cities</div></div><div style="font-size:2rem;">📍</div>
            </div>
            <div style="display:flex; align-items:center; gap:12px; background:rgba(255,255,255,0.9); backdrop-filter:blur(10px); border:1px solid rgba(239,79,95,0.15); border-radius:16px; padding:18px 26px; box-shadow:0 4px 20px rgba(239,79,95,0.12);">
                <div><div style="font-weight:800; font-size:1.5rem; color:#1c1c1c;">3 billion+</div><div style="font-size:0.9rem; color:#999; font-weight:500;">orders delivered</div></div><div style="font-size:2rem;">📦</div>
            </div>
        </div>
    </div>
    <br><br>
    """, unsafe_allow_html=True)

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
            h2 {{ text-align:center; font-weight:800; font-size:2.2rem; color:#1c1c1c; margin-bottom:8px; letter-spacing:-1px; }}
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

