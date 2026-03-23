import io
import json
import requests
import streamlit as st
import re
import time
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------
# 🔧 PAGE CONFIG + CYBER-DARK THEME (BLACK/CYAN)
# --------------------------------------
st.set_page_config(
    page_title="Pictator Pro: CEO Engineering Suite",
    page_icon="🏎️",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;700&display=swap');
    
    /* Global Background & Font */
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #00eaff !important; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Technical Metadata Cards */
    .car-card { border: 1px solid #333333; border-radius: 4px; padding: 15px; margin-bottom: 15px; background: #0a0a0a; box-shadow: 0 4px 15px rgba(0,234,255,0.05); transition: transform 0.3s ease;}
    .car-card:hover { transform: translateY(-3px); border-color: #00eaff; }
    
    .label-header { color: #ffffff; font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 18px; border-bottom: 1px solid #222; margin-bottom: 10px; padding-bottom: 5px;}
    .meta-label { color: #00eaff; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-top: 8px; letter-spacing: 1px;}
    .meta-value { color: #ffffff; font-family: 'Inter', sans-serif; font-size: 14px; margin-bottom: 8px; }
    
    /* UI Container Box */
    .ui-box { border: 1px solid #00eaff; border-radius: 8px; padding: 25px; background: #050505; margin-top: 20px; }
    .rca-box { border-left: 4px solid #ff00ff; padding: 20px; background: #0a0a0a; margin-bottom: 25px; font-family: 'Inter', sans-serif; line-height: 1.6; color: #eee; }
    
    /* Action Buttons */
    .stButton>button { 
        background: linear-gradient(90deg, #00eaff, #0072ff); 
        color: #000000 !important; font-weight: 800; border: none; border-radius: 4px; width: 100%; height: 50px; text-transform: uppercase;
    }
    .stTextArea textarea { background-color: #0a0a0a !important; color: #ffffff !important; border: 1px solid #333333 !important; font-family: 'Inter', sans-serif; }
    
    /* Resource Link Buttons */
    .stLinkButton > a { background-color: #ffffff !important; color: #000000 !important; font-weight: 700 !important; border-radius: 2px !important; }
    </style>
    <h1 style='text-align:center;'>🏎️ Pictator Pro – CEO Engineering Suite</h1>
    <h3 style='text-align:center;color:#888888;font-size:16px;'>Board-Level RCA | Dynamic Design | 2026 Material Intelligence</h3>
    <hr style='border:1px solid #222'>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# 🔵 USAGE TRACKER
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
# SIDEBAR LOGIN
# --------------------------------------
st.sidebar.title("🔐 User Dashboard")
if st.session_state.logged_in:
    user = st.session_state.current_user
    st.sidebar.success(f"User: {user}")
    user_stats = usage_store["users"].get(user, {"count": 0, "last": "No history"})
    st.sidebar.metric("Generations", user_stats["count"])
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
    st.warning("🔑 Please login to access the Strategic Analysis Suite.")
    st.stop()

# =====================================================================
# 🛰️ ENGINES (OpenRouter, SerpAPI, HF)
# =====================================================================

ANALYSIS_FALLBACK_MODELS = [
    "openai/gpt-oss-20b:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "x-ai/grok-4.1-fast:free",
]

def call_openrouter_fallback(prompt):
    """Iterates through models to ensure technical data is retrieved."""
    for model in ANALYSIS_FALLBACK_MODELS:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}]}, timeout=20)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except: continue
    return "Error: All analysis models timed out. Please verify API key."

def get_serp_images(query):
    params = {"engine": "google_images", "q": query, "api_key": SERP_API_KEY}
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        return resp.json().get("images_results", [])[:3]
    except: return []

def hf_gen_image(prompt, width=1024, height=512):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        resp = requests.post(url, headers=headers, json={"inputs": prompt, "parameters": {"width": width, "height": height}}, timeout=60)
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except: return None

# =====================================================================
# 🎨 MAIN UI EXECUTION
# =====================================================================
prompt = st.text_area("CEO Engineering Prompt / RCA Topic", placeholder="Enter technical failure description or part design requirements...")

col_btn1, col_btn2 = st.columns(2)

if col_btn1.button("🚀 EXECUTE FULL STRATEGIC ANALYSIS"):
    if not prompt: st.error("Please enter a prompt to begin.")
    else:
        st.markdown("---")
        with st.spinner("Processing Global Engineering Intelligence..."):
            # 1. Root Cause Analysis
            rca_query = f"Perform CEO-level RCA for: {prompt}. Use Engineering Science, Physics, and 2026 Evidence. Formal Board tone."
            rca_intel = call_openrouter_fallback(rca_query)
            
            # 2. Dynamic Component Metadata
            meta_query = f"Return ONLY a JSON list of 3 automotive variations for '{prompt}'. Keys: Brand, Country, Type, Material, Strength."
            specs_raw = call_openrouter_fallback(meta_query)
            
            # 3. Market Photos & AI Concepts
            market_photos = get_serp_images(f"{prompt} 2026 industry technical")
            ai_concept = hf_gen_image(f"Automotive engineering comparison split view, {prompt}, realistic, 8k")

            # --- DISPLAY RCA ---
            st.markdown("<div class='rca-box'><h3>STRATEGIC ROOT CAUSE ANALYSIS</h3>" + rca_intel + "</div>", unsafe_allow_html=True)
            
            # --- DISPLAY AI CONCEPT ---
            if ai_concept:
                st.image(ai_concept, caption="AI Concept Design Matrix (Structural Breakdown)", use_column_width=True)

            # --- DISPLAY DYNAMIC DATA MATRIX ---
            st.markdown("<div class='ui-box'><h3>🔍 Technical Markings & Real-World References</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            
            # Safe Regex Parse for JSON
            try:
                match = re.search(r'\[.*\]', specs_raw, re.DOTALL)
                specs = json.loads(match.group()) if match else []
            except: specs = []

            for i, col in enumerate(cols):
                with col:
                    if i < len(specs):
                        data = specs[i]
                        st.markdown(f"<div class='car-card'><div class='label-header'>{data.get('Brand','N/A')}</div>", unsafe_allow_html=True)
                        if i < len(market_photos):
                            st.image(market_photos[i]['thumbnail'], use_column_width=True)
                            st.link_button("View Intelligence 🔗", market_photos[i]['link'], use_container_width=True)
                        
                        for k in ["Country", "Type", "Material", "Strength"]:
                            st.markdown(f"<div class='meta-label'>{k}</div><div class='meta-value'>{data.get(k,'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# 🚀 FINAL RENDER SYSTEM (Separate for high-res output)
if col_btn2.button("📷 GENERATE HIGH-RES 3D RENDER"):
    if not prompt: st.error("Enter a prompt.")
    else:
        with st.spinner("Rendering Board-Ready 3D Visual..."):
            render = hf_gen_image(f"Professional automotive 3D render, {prompt}, cinematic, 8k", width=1024, height=1024)
            if render:
                update_usage(st.session_state.current_user)
                st.image(render, caption="Final Engineering Render", use_column_width=True)
                buf = io.BytesIO()
                render.save(buf, format="PNG")
                st.download_button("💾 Download Render", buf.getvalue(), "engineering_render.png")

# --- DYNAMIC INTELLIGENCE FOOTER ---
if prompt:
    st.markdown("---")
    st.subheader(f"🌐 Intelligence Hub: {prompt[:30]}")
    fcols = st.columns(4)
    links = [
        {"l": "YouTube Trends", "u": f"https://www.youtube.com/results?search_query={prompt.replace(' ','+')}+2026+engineering"},
        {"l": "Material Specs", "u": f"https://www.google.com/search?q={prompt.replace(' ','+')}+material+data+sheet+physics"},
        {"l": "Market Costs", "u": f"https://www.google.com/search?q={prompt.replace(' ','+')}+price+india+2026"},
        {"l": "Global Standards", "u": f"https://www.google.com/search?q={prompt.replace(' ','+')}+AIS+safety+standards"}
    ]
    for i, link in enumerate(links):
        fcols[i].link_button(link["l"], link["u"], use_container_width=True)
