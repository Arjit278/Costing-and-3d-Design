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
    </style>
    <h1 style='text-align:center;color:#00eaff;font-size:45px;'>🏎️ Pictator Creator – Automotive 3D Edition</h1>
    <h3 style='text-align:center;color:#ffffff;'>Multi-User | Trend Design | Engineering Graphics</h3>
    <hr style='border:1px solid #333'>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# 🔵 GLOBAL USAGE TRACKER (Sidebar Visible)
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
# SIDEBAR LOGIN & HISTORY COUNTER
# --------------------------------------
st.sidebar.title("🔐 User Dashboard")

if st.session_state.logged_in:
    user = st.session_state.current_user
    st.sidebar.success(f"User: {user}")
    
    # --- 📸 IMAGE GENERATION COUNTER ---
    user_stats = usage_store["users"].get(user, {"count": 0, "last": "No history"})
    st.sidebar.markdown("### 📊 Your History")
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
# 🛰️ ENGINES (HF & OPENROUTER FREE MODELS)
# =====================================================================
OR_MODELS = [
    "x-ai/grok-4.1-fast:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nvidia/nemotron-nano-12b-v2-vl:free"
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

# =====================================================================
# 🎨 MAIN UI - DESIGN & TRENDS
# =====================================================================
MODELS = {
    "Realistic Vision V6 (Automotive)": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
    "Flux.1-Schnell (Ultra Fast)": "black-forest-labs/FLUX.1-schnell",
    "Automotive 3D (Refined)": "stabilityai/stable-diffusion-3-medium-diffusers",
}

model_choice = st.selectbox("Select Model Engine", list(MODELS.keys()))
prompt = st.text_area("Engineering / Design Prompt", "premium nappa leather seat covers, diamond stitching, beige and black dual tone")

# --- TRENDS & SEARCH MATRIX BLOCK ---
if prompt and any(x in prompt.lower() for x in ["design", "reference", "car", "cover", "part"]):
    st.markdown("---")
    st.subheader("📸 AI Trend & Market Analysis (Simultaneous)")
    
    # OpenRouter Logic with Free Model Failover
    trend_text = "Sustainable luxury, breathable materials."
    with st.spinner("Analyzing Materials (OpenRouter)..."):
        for model in OR_MODELS:
            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                    json={"model": model, "messages": [{"role": "user", "content": f"Briefly list materials and 2026 trends for: {prompt}"}]}
                )
                if r.status_code == 200:
                    trend_text = r.json()["choices"][0]["message"]["content"]
                    break
            except: continue

    # HF Generation
    merged_prompt = f"Automotive part photography. Left: Premium. Center: Modern. Right: Tech. {prompt}. 8k, realistic."
    with st.spinner("Generating Design Concepts (HuggingFace)..."):
        out_ai = hf_router_generate_image("black-forest-labs/FLUX.1-schnell", merged_prompt, width=1024, height=512)

    if out_ai and out_ai["type"] == "image":
        st.image(out_ai["data"], caption="AI Concept Design Matrix", use_column_width=True)

    # Reference Search Box
    st.markdown("### 🔍 Real-World Product Reference & Purchase Links")
    ref_photos = get_serp_images(f"{prompt} for cars 2026 price")
    cols = st.columns(3)
    
    car_meta = [
        {"name": "Elegant Auto", "origin": "India 🇮🇳", "mat": "Nappa Leatherette", "tier": "Premium"},
        {"name": "Tessories", "origin": "Global 🌍", "mat": "Vegan Microfiber", "tier": "High-Tech"},
        {"name": "Autoform", "origin": "India 🇮🇳", "mat": "PU Dry-Feel", "tier": "Economy Plus"}
    ]
    
    for i, col in enumerate(cols):
        with col:
            meta = car_meta[i]
            st.markdown(f"""
                <div class='car-card'>
                    <div class='label-header'>{meta['name']}</div>
                    <div class='meta-label'>Region</div><div class='meta-value'>{meta['origin']}</div>
                    <div class='meta-label'>Primary Material</div><div class='meta-value'>{meta['mat']}</div>
                    <div class='meta-label'>Market Segment</div><div class='meta-value'>{meta['tier']}</div>
                </div>
            """, unsafe_allow_html=True)
            if i < len(ref_photos):
                st.image(ref_photos[i]['thumbnail'], use_column_width=True)
                st.markdown(f"[🛒 View Product & Price]({ref_photos[i]['link']})")

# --- FINAL GENERATION ---
st.markdown("---")
if st.button("🚀 Finalize Engineering Render"):
    with st.spinner("Rendering..."):
        res = hf_router_generate_image(MODELS[model_choice], prompt)
        if res and res["type"] == "image":
            update_usage(st.session_state.current_user)
            st.image(res["data"], caption="Final Rendered Output", use_column_width=True)
            st.success("Generation added to your user history!")
