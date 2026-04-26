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

# ══════════════════════════════════════════════════════════════════════
#  HERO SECTION — AT THE TOP
# ══════════════════════════════════════════════════════════════════════
HERO_HTML = """
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Poppins',sans-serif;
       background: linear-gradient(160deg, #ffd6e0 0%, #ffafc5 20%, #ffc2d1 40%, #ff8fab 60%, #ffb3c6 80%, #ffc2d1 100%);
       overflow-x:hidden; }

.hero { position:relative; width:100%; min-height:1000px; display:flex; flex-direction:column;
        align-items:center; justify-content:center; padding:50px 20px; overflow:hidden; }

/* Decorative animated circles */
.circle { position:absolute; border-radius:50%; border:2px solid rgba(239,79,95,0.2); animation:drift 20s ease-in-out infinite; }
.circle.c1 { width:450px; height:450px; top:-100px; left:-80px; background:radial-gradient(circle,rgba(255,143,171,0.08),transparent); }
.circle.c2 { width:550px; height:550px; bottom:-150px; right:-120px; animation-direction:alternate-reverse; animation-delay:2s; background:radial-gradient(circle,rgba(239,79,95,0.06),transparent); }
.circle.c3 { width:350px; height:350px; top:25%; right:-60px; border-color:rgba(239,79,95,0.12); animation-delay:4s; }
.circle.c4 { width:250px; height:250px; bottom:18%; left:3%; border-color:rgba(255,150,170,0.2); animation-delay:6s; }
.circle.c5 { width:180px; height:180px; top:10%; left:40%; border-color:rgba(255,105,135,0.1); animation-delay:3s; }

@keyframes drift {
    0%   { transform: translate(0, 0) rotate(0deg) scale(1); }
    50%  { transform: translate(30px, -20px) rotate(10deg) scale(1.03); }
    100% { transform: translate(-10px, 15px) rotate(-5deg) scale(0.98); }
}

/* Kawaii food character container */
.food-char { position:absolute; z-index:3; display:flex; flex-direction:column; align-items:center;
             animation:floatBounce 4s ease-in-out infinite; }
.food-char .emoji { font-size:56px; filter:drop-shadow(0 6px 16px rgba(0,0,0,0.12));
                    position:relative; display:inline-block; }
.food-char .face { position:absolute; top:50%; left:50%; transform:translate(-50%,-55%);
                   font-size:14px; line-height:1; pointer-events:none; text-shadow:0 1px 2px rgba(0,0,0,0.2); }
.food-char .wave { font-size:22px; position:absolute; top:-8px; right:-18px;
                   animation:waveHand 1s ease-in-out infinite; transform-origin:bottom center; }
.food-char .bubble { background:#fff; border-radius:14px; padding:3px 10px; font-size:0.7rem;
                     font-weight:700; color:#ef4f5f; margin-bottom:4px; box-shadow:0 2px 8px rgba(239,79,95,0.15);
                     position:relative; white-space:nowrap; animation:popIn 0.5s ease-out; }
.food-char .bubble::after { content:''; position:absolute; bottom:-5px; left:50%; transform:translateX(-50%);
                            border-left:5px solid transparent; border-right:5px solid transparent;
                            border-top:6px solid #fff; }

@keyframes waveHand {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(25deg); }
    50% { transform: rotate(-10deg); }
    75% { transform: rotate(20deg); }
}

@keyframes floatBounce {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    25%      { transform: translateY(-18px) rotate(-4deg); }
    50%      { transform: translateY(-28px) rotate(4deg); }
    75%      { transform: translateY(-12px) rotate(-2deg); }
}

/* Position each food character */
.food-char.f1  { top:4%;  left:3%;  animation-delay:0s; }
.food-char.f2  { top:3%;  right:5%; animation-delay:0.6s; }
.food-char.f3  { top:16%; left:12%; animation-delay:1.2s; }
.food-char.f4  { top:12%; right:14%;animation-delay:1.8s; }
.food-char.f5  { bottom:32%; left:2%;animation-delay:0.3s; }
.food-char.f6  { bottom:28%; right:3%;animation-delay:1.5s; }
.food-char.f7  { top:38%; left:1%;  animation-delay:2.4s; }
.food-char.f8  { top:34%; right:2%; animation-delay:2s; }
.food-char.f9  { bottom:14%; left:8%;animation-delay:0.9s; }
.food-char.f10 { bottom:16%; right:10%;animation-delay:2.7s; }
.food-char.f11 { top:52%; left:6%; animation-delay:0.5s; }
.food-char.f12 { top:56%; right:7%;animation-delay:2.2s; }
.food-char.f13 { top:25%; left:1%; animation-delay:3s; }
.food-char.f14 { bottom:8%; right:18%; animation-delay:1s; }
.food-char.f15 { top:68%; left:2%; animation-delay:3.3s; }
.food-char.f16 { top:45%; right:1%; animation-delay:1.4s; }

.food-char.f1 .emoji, .food-char.f2 .emoji { font-size:64px; }
.food-char.f5 .emoji, .food-char.f6 .emoji { font-size:58px; }
.food-char.f13 .emoji,.food-char.f14 .emoji { font-size:52px; }

/* Floating hearts */
.heart { position:absolute; z-index:1; font-size:20px; opacity:0.5; animation:heartFloat 6s ease-in-out infinite; }
.heart.h1 { top:6%; left:25%; animation-delay:0s; font-size:18px; }
.heart.h2 { top:18%; right:25%; animation-delay:1.5s; font-size:22px; }
.heart.h3 { bottom:22%; left:30%; animation-delay:3s; font-size:16px; }
.heart.h4 { top:42%; right:20%; animation-delay:0.8s; font-size:20px; }
.heart.h5 { bottom:35%; right:28%; animation-delay:2.2s; font-size:14px; }
.heart.h6 { top:62%; left:22%; animation-delay:4s; font-size:18px; }
.heart.h7 { top:30%; left:35%; animation-delay:1s; font-size:15px; }
.heart.h8 { bottom:10%; left:45%; animation-delay:2.5s; font-size:20px; }

@keyframes heartFloat {
    0%, 100% { transform: translateY(0) scale(1); opacity:0.4; }
    50%      { transform: translateY(-20px) scale(1.2); opacity:0.7; }
}

/* sparkle particles */
.sparkle { position:absolute; width:6px; height:6px; background:#ef4f5f; border-radius:50%;
           opacity:0.4; animation:twinkle 3s ease-in-out infinite; }
.sparkle.s1 { top:10%; left:30%; }
.sparkle.s2 { top:22%; right:28%; animation-delay:1s; width:4px; height:4px; }
.sparkle.s3 { bottom:30%; left:22%; animation-delay:2s; width:5px; height:5px; }
.sparkle.s4 { top:48%; right:22%; animation-delay:0.5s; }
.sparkle.s5 { bottom:18%; left:38%; animation-delay:1.5s; width:4px; height:4px; }
.sparkle.s6 { top:65%; right:32%; animation-delay:2.5s; width:5px; height:5px; }
.sparkle.s7 { top:8%; left:50%; animation-delay:0.3s; width:5px; height:5px; background:#ff6b81; }
.sparkle.s8 { bottom:40%; right:15%; animation-delay:1.8s; width:7px; height:7px; background:#ff4757; }
.sparkle.s9 { top:75%; left:15%; animation-delay:3s; width:4px; height:4px; }
.sparkle.s10{ bottom:5%; right:40%; animation-delay:0.7s; width:6px; height:6px; background:#ff6b81; }

@keyframes twinkle {
    0%, 100% { opacity:0.2; transform:scale(1); }
    50%      { opacity:0.8; transform:scale(2); }
}

@keyframes popIn {
    0% { transform:scale(0); opacity:0; }
    80% { transform:scale(1.1); }
    100% { transform:scale(1); opacity:1; }
}

.title { font-weight:800; font-size:3.4rem; color:#1c1c1c; text-align:center; line-height:1.15; z-index:4; position:relative; }
.title span { color:#ef4f5f; }
.subtitle { font-weight:300; font-size:1.1rem; color:#444; text-align:center;
            max-width:500px; margin:20px auto 0; line-height:1.7; z-index:4; position:relative; }
.vid-wrap { position:relative; z-index:4; margin-top:40px; border-radius:20px; overflow:hidden;
            box-shadow:0 20px 60px rgba(239,79,95,0.28); width:720px; max-width:90%;
            border: 3px solid rgba(239,79,95,0.2); }
.vid-wrap video { width:100%; display:block; border-radius:18px; }
.stats { display:flex; justify-content:center; gap:40px; margin-top:50px; z-index:4; position:relative; flex-wrap:wrap; }
.stat { display:flex; align-items:center; gap:12px; background:rgba(255,255,255,0.9); backdrop-filter:blur(10px);
        border:1px solid rgba(239,79,95,0.15); border-radius:16px; padding:18px 26px;
        box-shadow:0 4px 20px rgba(239,79,95,0.12); }
.stat-n { font-weight:700; font-size:1.4rem; color:#1c1c1c; }
.stat-l { font-size:0.82rem; color:#999; }
.stat-i { font-size:1.8rem; }
</style></head><body>
<div class="hero">
    <!-- Decorative circles -->
    <div class="circle c1"></div>
    <div class="circle c2"></div>
    <div class="circle c3"></div>
    <div class="circle c4"></div>
    <div class="circle c5"></div>

    <!-- Sparkle particles -->
    <div class="sparkle s1"></div><div class="sparkle s2"></div><div class="sparkle s3"></div>
    <div class="sparkle s4"></div><div class="sparkle s5"></div><div class="sparkle s6"></div>
    <div class="sparkle s7"></div><div class="sparkle s8"></div><div class="sparkle s9"></div>
    <div class="sparkle s10"></div>

    <!-- Floating hearts -->
    <div class="heart h1">💕</div><div class="heart h2">💗</div><div class="heart h3">💖</div>
    <div class="heart h4">💕</div><div class="heart h5">💗</div><div class="heart h6">💖</div>
    <div class="heart h7">💕</div><div class="heart h8">💗</div>

    <!-- Cute kawaii food characters with faces waving hi -->
    <div class="food-char f1">
        <div class="bubble">Hi! 😊</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍔</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f2">
        <div class="bubble">Hey! 🥰</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍕</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f3">
        <div class="bubble">Hiii!</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍩</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f4">
        <div class="bubble">Hello! 😋</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍣</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f5">
        <div class="bubble">Yoo! 🎉</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🌮</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f6">
        <div class="bubble">Hi there!</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍰</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f7">
        <div class="bubble">Heyyy! 😄</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🧁</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f8">
        <div class="bubble">Namaste!</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍜</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f9">
        <div class="bubble">Hi! 🍦</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍦</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f10">
        <div class="bubble">Bonjour!</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🥐</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f11">
        <div class="bubble">Hey! 🍿</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍿</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f12">
        <div class="bubble">Hola! 🥗</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🥗</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f13">
        <div class="bubble">Yo! 😎</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍟</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f14">
        <div class="bubble">Hi hi!</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍪</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f15">
        <div class="bubble">Ciao! 🤗</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🥞</span><span class="wave">👋</span></div>
    </div>
    <div class="food-char f16">
        <div class="bubble">Heyy!</div>
        <div style="position:relative;display:inline-block"><span class="emoji">🍡</span><span class="wave">👋</span></div>
    </div>

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
components.html(HERO_HTML, height=1050, scrolling=False)


# Hide default chrome + custom widget styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 0 !important; max-width: 100% !important;}
.stApp {
    background: linear-gradient(160deg, #ffd6e0 0%, #ffafc5 20%, #ffc2d1 40%, #ff8fab 60%, #ffb3c6 80%, #ffc2d1 100%) !important;
    font-family: 'Poppins', sans-serif;
}
.stSelectbox > div > div { border-radius: 10px !important; background: rgba(255,255,255,0.9) !important; }
.stTextInput > div > div > input { border-radius: 10px !important; background: rgba(255,255,255,0.9) !important; }
.stButton > button {
    background: linear-gradient(135deg, #ef4f5f, #e8364a) !important; color: white !important; border: none !important;
    border-radius: 12px !important; font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important; font-size: 1.05rem !important;
    padding: 0.7rem 2rem !important; width: 100% !important;
    box-shadow: 0 4px 15px rgba(239,79,95,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #d64550, #c42f3e) !important;
    box-shadow: 0 8px 25px rgba(239,79,95,0.4) !important;
    transform: translateY(-1px);
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

