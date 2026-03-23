import io
import base64
import requests
import streamlit as st
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------
# 🔧 PAGE CONFIG + THEME
# --------------------------------------
st.set_page_config(
    page_title="Pictator Creator - Automotive 3D",
    page_icon="⚙️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .car-card { border: 2px solid #00eaff; border-radius: 10px; padding: 15px; margin: 10px; background: #1a1c24; }
    .label-header { color: #00eaff; font-weight: bold; font-size: 18px; margin-bottom: 5px; }
    </style>
    <h1 style='text-align:center;color:#00eaff;font-size:45px;'>⚙️ Pictator Creator – Automotive 3D Edition</h1>
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

def now_ist_string():
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")

def update_usage(username):
    usage_store["total"] += 1
    if username not in usage_store["users"]:
        usage_store["users"][username] = {"count": 0, "last": None}
    usage_store["users"][username]["count"] += 1
    usage_store["users"][username]["last"] = now_ist_string()

# =====================================================================
# 🔐 AUTHENTICATION & SECRETS
# =====================================================================
if "users" not in st.session_state:
    st.session_state.users = dict(st.secrets.get("users", {"admin": "harmony2026"}))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Hardcoded keys as per request or fallback to secrets
OPENROUTER_API_KEY = "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"
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "") 
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --------------------------------------
# SIDEBAR LOGIN & ADMIN
# --------------------------------------
st.sidebar.title("🔐 Login Panel")

if st.session_state.logged_in:
    st.sidebar.success(f"User: {st.session_state.current_user}")
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
        else: st.sidebar.error("Invalid credentials")

# Stop if not logged in
if not st.session_state.logged_in:
    st.warning("🔑 Please login to access the Automotive Design Suite.")
    st.stop()

# =====================================================================
# 🛰️ HELPER ENGINES
# =====================================================================

def get_serp_images(query):
    params = {"engine": "google_images", "q": query, "api_key": SERP_API_KEY}
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        return resp.json().get("images_results", [])[:3]
    except: return []

def hf_router_generate_image(model_repo, prompt, width=1024, height=1024, steps=30, guidance=3.5):
    url = f"https://router.huggingface.co/hf-inference/models/{model_repo}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"width": width, "height": height, "num_inference_steps": steps, "guidance_scale": guidance}}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            return {"type": "image", "data": Image.open(io.BytesIO(resp.content)).convert("RGB")}
    except Exception as e: return {"type": "error", "data": str(e)}
    return {"type": "error", "data": "Failed to generate image"}

# =====================================================================
# 🎨 MAIN UI - DESIGN & TRENDS
# =====================================================================
MODELS = {
    "Sketchers (Lineart / Mechanical)": "black-forest-labs/FLUX.1-dev",
    "CAD Drawing XL (2D Blueprints)": "stabilityai/stable-diffusion-xl-base-1.0",
    "RealisticVision (Automotive 3D)": "stabilityai/stable-diffusion-3-medium-diffusers",
}

model_choice = st.selectbox("Select Model Engine", list(MODELS.keys()))
prompt = st.text_area("Engineering / Design Prompt", "luxury sedan chassis design, 3D render, carbon fiber textures")

# --- TRENDS & SEARCH MATRIX BLOCK ---
if prompt and any(x in prompt.lower() for x in ["design", "reference", "photograph", "car"]):
    st.markdown("---")
    st.subheader("📸 AI Trend-Based Market Comparison")
    
    with st.spinner("Analyzing Global 2025 Trends..."):
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": "List 3 car trends 2025 for: " + prompt}]}
            )
            trend_text = r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else "Standard 2025 Automotive Trends"
        except: trend_text = "Standard 2025 Automotive Trends"

    # AI Visual Comparison
    merged_prompt = f"Split image 3 sections. LEFT: BMW (Germany). CENTER: Toyota (Japan). RIGHT: Tesla (USA). Realistic, labeled. Trends: {trend_text}"
    with st.spinner("Generating Design Matrix..."):
        out_ai = hf_router_generate_image("stabilityai/stable-diffusion-3-medium-diffusers", merged_prompt, width=1024, height=512)

    if out_ai["type"] == "image":
        st.image(out_ai["data"], caption="AI Trend Comparison: Germany | Japan | USA", use_column_width=True)

    # Reference Search Box
    st.markdown("### 🔍 Real-World Reference Matrix")
    ref_photos = get_serp_images(f"{prompt} 2025 car design")
    cols = st.columns(3)
    car_meta = [
        {"name": "BMW i7", "origin": "Germany 🇩🇪", "cat": "Luxury"},
        {"name": "Toyota Prius", "origin": "Japan 🇯🇵", "cat": "Efficiency"},
        {"name": "Tesla Model 3", "origin": "USA 🇺🇸", "cat": "Tech"}
    ]
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"<div class='car-card'><div class='label-header'>{car_meta[i]['name']}</div>"
                        f"<b>Origin:</b> {car_meta[i]['origin']}<br><b>Cat:</b> {car_meta[i]['cat']}</div>", unsafe_allow_html=True)
            if i < len(ref_photos):
                st.image(ref_photos[i]['thumbnail'], use_column_width=True)
                st.markdown(f"[🔗 Source]({ref_photos[i]['link']})")

# --- FINAL GENERATION BUTTON ---
st.markdown("---")
col_w, col_h, col_s, col_g = st.columns(4)
width = col_w.number_input("Width", 256, 1536, 1024)
height = col_h.number_input("Height", 256, 1536, 768)
steps = col_s.slider("Steps", 10, 50, 30)
guidance = col_g.slider("Guidance", 1.0, 10.0, 3.5)

if st.button("🚀 Finalize Generation"):
    with st.spinner("Rendering High-Resolution Output..."):
        res = hf_router_generate_image(MODELS[model_choice], prompt, width, height, steps, guidance)
        update_usage(st.session_state.current_user)
        
        if res["type"] == "image":
            st.image(res["data"], caption="Final Pictator Render", use_column_width=True)
            buf = io.BytesIO()
            res["data"].save(buf, format="PNG")
            st.download_button("💾 Download Render", buf.getvalue(), "render.png", "image/png")
        else: st.error(res["data"])
