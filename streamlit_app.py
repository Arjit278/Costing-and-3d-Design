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
    .meta-label { color: #00eaff; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-top: 8px;}
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
                json={"model": model, "messages": [{"role": "user", "content": f"Analyze {prompt} for 2026. Provide technical details for: Brand, Type, Materials, Strength, and Country."}]},
                timeout=15)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
        except: continue
    return "2026 Material Trend: High-tensile vegan polymers and carbon-reinforced textures."

# =====================================================================
# 🎨 MAIN UI
# =====================================================================
MODELS = {
    "Realistic Vision V6 (Automotive)": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
    "Flux.1-Schnell (Ultra Fast)": "black-forest-labs/FLUX.1-schnell",
    "Automotive 3D (Refined)": "stabilityai/stable-diffusion-3-medium-diffusers",
}

model_choice = st.selectbox("Select Model Engine", list(MODELS.keys()))
prompt = st.text_area("Engineering / Design Prompt", placeholder="e.g. Nappa leather seat covers for BMW i7, diamond stitching...")

col_btn1, col_btn2 = st.columns(2)

# --- 📸 ANALYSIS SYSTEM ---
if col_btn1.button("🔍 Run Trend & Market Analysis"):
    if not prompt:
        st.error("Please enter a prompt to analyze.")
    else:
        st.markdown("---")
        with st.spinner("Processing Global Intelligence (OpenRouter + Search + HF)..."):
            tech_specs = get_openrouter_intel(prompt)
            market_data = get_serp_images(f"{prompt} 2026 luxury automotive")
            merged_prompt = f"3-way split comparison. Automotive part design. Left: Premium. Center: Eco. Right: Sport. {prompt}. 8k, photorealistic."
            out_ai = hf_router_generate_image("black-forest-labs/FLUX.1-schnell", merged_prompt, width=1024, height=512)

            if out_ai and out_ai["type"] == "image":
                st.image(out_ai["data"], caption="AI Concept Design Matrix", use_column_width=True)

            # --- RENDER MARKET MATRIX WITH ALL 5 FIELDS ---
            st.markdown("<div class='ui-box'>", unsafe_allow_html=True)
            st.subheader("🔍 Real-World Product Reference & Purchase Links")
            cols = st.columns(3)
            car_meta = [
                {"brand": "Elegant Auto", "origin": "India 🇮🇳", "type": "Luxury Bespoke", "mat": "Nappa Leatherette", "strength": "High-Durability"},
                {"brand": "Tessories", "origin": "Global 🌍", "type": "Tech-Integrated", "mat": "Vegan Microfiber", "strength": "Abrasion Resistant"},
                {"brand": "Autoform", "origin": "India 🇮🇳", "type": "Standard Performance", "mat": "PU Dry-Feel", "strength": "Daily Duty"}
            ]
            for i, col in enumerate(cols):
                with col:
                    meta = car_meta[i]
                    st.markdown(f"<div class='label-header'>{meta['brand']}</div>", unsafe_allow_html=True)
                    if i < len(market_data):
                        st.image(market_data[i]['thumbnail'], use_column_width=True)
                        st.link_button("View Product 🔗", market_data[i]['link'], use_container_width=True)
                    
                    st.markdown(f"<div class='meta-label'>Country</div><div class='meta-value'>{meta['origin']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='meta-label'>Part Type</div><div class='meta-value'>{meta['type']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='meta-label'>Material</div><div class='meta-value'>{meta['mat']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='meta-label'>Strength</div><div class='meta-value'>{meta['strength']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.subheader("📝 OpenRouter Technical Specifications")
            st.info(tech_specs)

# --- 🚀 FINAL RENDER SYSTEM ---
if col_btn2.button("🚀 Finalize Engineering Render"):
    if not prompt:
        st.error("Please enter a prompt to render.")
    else:
        st.markdown("---")
        with st.spinner("Rendering High-Resolution Output..."):
            res = hf_router_generate_image(MODELS[model_choice], prompt)
            if res and res["type"] == "image":
                update_usage(st.session_state.current_user)
                st.image(res["data"], caption="Final Rendered Output", use_column_width=True)
                buf = io.BytesIO()
                res["data"].save(buf, format="PNG")
                st.download_button("💾 Download PNG", buf.getvalue(), "render.png", "image/png")
                st.success("Generation tracked in your history!")

# --- DYNAMIC FOOTER RESOURCES (Inside the Button Logic) ---
st.markdown("---")
st.subheader(f"🌐 Global Trend Inspiration: {prompt[:30]}...")

# Generate Dynamic Queries based on the User Prompt
dynamic_queries = [
    {"type": "YouTube", "label": "Latest Trends", "query": f"{prompt} 2026 design trends"},
    {"type": "Market", "label": "Price Comparison", "query": f"best {prompt} price india 2026"},
    {"type": "Engineering", "label": "Material Science", "query": f"{prompt} manufacturing material innovations"},
    {"type": "Global", "label": "International Brands", "query": f"top global brands for {prompt}"}
]

res_cols = st.columns(4)

for i, res in enumerate(dynamic_queries):
    # Constructing dynamic URLs
    if res["type"] == "YouTube":
        search_url = f"https://www.youtube.com/results?search_query={res['query'].replace(' ', '+')}"
    else:
        search_url = f"https://www.google.com/search?q={res['query'].replace(' ', '+')}"
    
    with res_cols[i]:
        st.link_button(
            f"🔗 {res['type']}: {res['label']}", 
            search_url, 
            use_container_width=True,
            help=f"Search for {res['query']}"
        )

# Optional: Add a specialized "Deep Dive" link for Material Science
st.markdown("""
    <div style='text-align: center; padding: 10px; background-color: #1a1c24; border-radius: 10px; border: 1px dashed #00eaff;'>
        <p style='margin: 0; font-size: 14px; color: #888;'>
            💡 <b>Pro Tip:</b> Click the <b>Material Science</b> button to see 2026 strength-to-weight ratio data for this part.
        </p>
    </div>
""", unsafe_allow_html=True)
