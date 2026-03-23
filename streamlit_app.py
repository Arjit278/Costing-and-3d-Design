import io
import base64
import requests
import streamlit as st
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------
# 🔧 PAGE CONFIG + THEME + STYLING
# --------------------------------------
st.set_page_config(
    page_title="Pictator Creator - Automotive 3D Pro",
    page_icon="🏎️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .car-card { border: 2px solid #00eaff; border-radius: 12px; padding: 15px; margin: 10px; background: #1a1c24; box-shadow: 0 4px 15px rgba(0,234,255,0.2); }
    .label-header { color: #00eaff; font-weight: bold; font-size: 20px; border-bottom: 1px solid #333; margin-bottom: 10px; }
    .meta-label { color: #888; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .meta-value { color: #fff; font-size: 14px; margin-bottom: 8px; }
    .ui-box { border: 2px solid #00eaff; border-radius: 15px; padding: 20px; background: #1a1c24; margin-bottom: 25px; }
    .spec-header { color: #00eaff; font-size: 14px; font-weight: bold; text-transform: uppercase; margin-top: 10px; }
    .spec-text { color: #ffffff; font-size: 15px; margin-bottom: 10px; }
    </style>
    <h1 style='text-align:center;color:#00eaff;font-size:45px;'>🏎️ Pictator Creator – Automotive 3D Edition</h1>
    <h3 style='text-align:center;color:#ffffff;'>Multi-User | Trend Design | Engineering Graphics</h3>
    <hr style='border:1px solid #333'>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# 🔵 GLOBAL USAGE TRACKER
# =====================================================================
@st.cache_resource
def init_usage_store():
    return {"total": 0, "users": {}}

usage_store = init_usage_store()
KOLKATA_TZ = ZoneInfo("Asia/Kolkata")

def update_usage(username):
    usage_store["total"] += 1
    if username not in usage_store["users"]:
        usage_store["users"][username] = {"count": 0, "last": None}
    usage_store["users"][username]["count"] += 1
    usage_store["users"][username]["last"] = datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")

# =====================================================================
# 🔐 AUTHENTICATION & KEYS
# =====================================================================
if "users" not in st.session_state:
    st.session_state.users = dict(st.secrets.get("users", {"admin": "harmony2026"}))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

OPENROUTER_API_KEY = "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"
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "") 
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --------------------------------------
# SIDEBAR LOGIN & HISTORY
# --------------------------------------
st.sidebar.title("🔐 User Dashboard")

if st.session_state.logged_in:
    user = st.session_state.current_user
    st.sidebar.success(f"User: {user}")
    user_stats = usage_store["users"].get(user, {"count": 0, "last": "No history"})
    st.sidebar.metric("Images Generated", user_stats["count"])
    st.sidebar.caption(f"Last used: {user_stats['last']}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
else:
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.logged_in = True
            st.session_state.current_user = u
            st.rerun()

if not st.session_state.logged_in:
    st.warning("🔑 Please login to access the Automotive Design Suite.")
    st.stop()

# =====================================================================
# 🛰️ ENGINES
# =====================================================================
OR_MODELS = [
    "x-ai/grok-4.1-fast:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.2-3b-instruct:free"
]

def get_serp_images(query):
    params = {"engine": "google_images", "q": query, "api_key": SERP_API_KEY}
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        return resp.json().get("images_results", [])[:3]
    except: return []

def hf_router_generate_image(model_repo, prompt, width=1024, height=1024):
    url = f"https://router.huggingface.co/hf-inference/models/{model_repo}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"width": width, "height": height}}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            return {"type": "image", "data": Image.open(io.BytesIO(resp.content)).convert("RGB")}
    except: return None
    return {"type": "error", "data": "HF Router Failed"}

def get_openrouter_intel(prompt):
    for model in OR_MODELS:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={"model": model, "messages": [{"role": "user", "content": f"Provide technical 2026 specs for {prompt}. Include Material, Brand, and Tier."}]},
                timeout=15)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
        except: continue
    return "Standard 2026 Automotive Trends: Lightweight Composites and Bio-Based Textures."

# =====================================================================
# 🎨 MAIN UI
# =====================================================================
MODELS = {
    "Realistic Vision V6 (Automotive)": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
    "Flux.1-Schnell (Ultra Fast)": "black-forest-labs/FLUX.1-schnell",
    "Automotive 3D (Refined)": "stabilityai/stable-diffusion-3-medium-diffusers",
}

model_choice = st.selectbox("Select Model Engine", list(MODELS.keys()))
# Prompt is blank by default
prompt = st.text_area("Engineering / Design Prompt", placeholder="e.g. Nappa leather seat covers for BMW i7, diamond stitching...")

col_btn1, col_btn2 = st.columns(2)

# --- 📸 ANALYSIS SYSTEM ---
if col_btn1.button("🔍 Run Trend & Market Analysis"):
    if not prompt:
        st.error("Please enter a prompt to analyze.")
    else:
        st.markdown("---")
        with st.spinner("Simultaneous Intelligence Processing (OpenRouter + Search + HF)..."):
            # Execute all three simultaneously
            tech_specs = get_openrouter_intel(prompt)
            market_data = get_serp_images(f"{prompt} 2026 luxury price")
            merged_prompt = f"Automotive part photography comparison. Left: Premium. Center: Modern. Right: Performance. {prompt}. 8k, realistic."
            out_ai = hf_router_generate_image("black-forest-labs/FLUX.1-schnell", merged_prompt, width=1024, height=512)

            # Display HF AI Comparison
            if out_ai and out_ai["type"] == "image":
                st.image(out_ai["data"], caption="AI Concept Design Matrix", use_column_width=True)

            # Display Market Matrix (UI Boxes)
            st.markdown("<div class='ui-box'>", unsafe_allow_html=True)
            st.subheader("🔍 Real-World Product Reference & Purchase Links")
            cols = st.columns(3)
            car_meta = [
                {"name": "Elegant Auto", "origin": "India 🇮🇳", "mat": "Nappa Leatherette", "tier": "Premium"},
                {"name": "Tessories", "origin": "Global 🌍", "mat": "Vegan Microfiber", "tier": "High-Tech"},
                {"name": "Autoform", "origin": "India 🇮🇳", "mat": "PU Dry-Feel", "tier": "Economy Plus"}
            ]
            for i, col in enumerate(cols):
                with col:
                    meta = car_meta[i]
                    st.markdown(f"**{meta['name']}**")
                    st.caption(f"{meta['origin']} | {meta['tier']}")
                    if i < len(market_data):
                        st.image(market_data[i]['thumbnail'], use_column_width=True)
                        st.link_button("View Product 🔗", market_data[i]['link'], use_container_width=True)
                    st.markdown(f"<div class='meta-label'>Material</div><div class='meta-value'>{meta['mat']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Display OpenRouter Specs
            st.subheader("📝 OpenRouter Technical Specifications")
            st.info(tech_specs)

# --- 🚀 FINAL RENDER SYSTEM ---
if col_btn2.button("🚀 Finalize Engineering Render"):
    if not prompt:
        st.error("Please enter a prompt to render.")
    else:
        st.markdown("---")
        with st.spinner("Rendering High-Resolution 3D Output..."):
            res = hf_router_generate_image(MODELS[model_choice], prompt)
            if res and res["type"] == "image":
                update_usage(st.session_state.current_user)
                st.image(res["data"], caption="Final Rendered Output", use_column_width=True)
                buf = io.BytesIO()
                res["data"].save(buf, format="PNG")
                st.download_button("💾 Download PNG", buf.getvalue(), "render.png", "image/png")
                st.success("Generation tracked in your history!")

# --- FOOTER RESOURCES ---
st.markdown("---")
st.subheader("🌐 Global Trend Inspiration")
res_cols = st.columns(4)
resources = [
    {"title": "Luxury Interiors 2026", "url": "https://www.youtube.com/results?search_query=luxury+car+interiors+2026+trends", "type": "YouTube"},
    {"title": "German Engineering Design", "url": "https://www.bmw.com/en/design.html", "type": "Website"},
    {"title": "Tesla Accessory Trends", "url": "https://www.tesla.com/shop", "type": "Website"},
    {"title": "Material Science Innovations", "url": "https://www.dezeen.com/tag/automotive-design/", "type": "Web Journal"}
]
for i, r_col in enumerate(res_cols):
    r_col.link_button(f"{resources[i]['type']}: {resources[i]['title']}", resources[i]['url'], use_container_width=True)
