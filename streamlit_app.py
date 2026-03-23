import io
import json
import requests
import streamlit as st
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------
# 🔧 PAGE CONFIG + CYBER-DARK THEME (BLACK/WHITE/CYAN)
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
    
    /* Strict Black & White Theme with Cyan Accents */
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #00eaff !important; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Technical Metadata Cards */
    .car-card { border: 1px solid #ffffff; border-radius: 4px; padding: 15px; margin: 10px; background: #111111; box-shadow: 0 4px 15px rgba(0,234,255,0.1); transition: transform 0.3s ease;}
    .car-card:hover { transform: translateY(-5px); border-color: #00eaff; }
    
    .label-header { color: #ffffff; font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 18px; border-bottom: 1px solid #333; margin-bottom: 10px; padding-bottom: 5px;}
    .meta-label { color: #00eaff; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-top: 8px; letter-spacing: 1px;}
    .meta-value { color: #ffffff; font-family: 'Inter', sans-serif; font-size: 14px; margin-bottom: 8px; font-weight: 400; }
    
    /* UI Container Box */
    .ui-box { border: 1px solid #333333; border-radius: 8px; padding: 25px; background: #0a0a0a; margin-top: 30px; }
    .rca-box { border-left: 4px solid #ffffff; padding-left: 20px; background: #050505; border-radius: 0 8px 8px 0; margin-bottom: 25px; font-family: 'Inter', sans-serif; line-height: 1.6; }
    
    /* Buttons: Cyan Gradient to Solid White Text */
    .stButton>button { 
        background: linear-gradient(90deg, #00eaff, #0072ff); 
        color: #000000 !important; font-weight: 800; border: none; border-radius: 4px; width: 100%; height: 50px; text-transform: uppercase;
    }
    .stTextArea textarea { background-color: #0a0a0a !important; color: #ffffff !important; border: 1px solid #333333 !important; font-family: 'Inter', sans-serif; }
    
    /* Link Buttons */
    .stLinkButton > a { background-color: #ffffff !important; color: #000000 !important; font-weight: 700 !important; border-radius: 2px !important; border: none !important; }
    </style>
    <h1 style='text-align:center;'>🏎️ Pictator Pro – CEO Engineering Suite</h1>
    <h3 style='text-align:center;color:#888888;'>Strategic RCA | Trend Design | Engineering Graphics</h3>
    <hr style='border:1px solid #222'>
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

def get_ceo_rca_analysis(topic):
    query = f"""
    Perform a CEO-level Root Cause Analysis (RCA) for: {topic}.
    Use Engineering Science (Physics, Stress, Chemistry), Material Science, and 2026 Industry Evidence.
    Structure the response for Board Review:
    1. Technical Fault Mechanism (Chemistry/Physics)
    2. Material Lifecycle Degradation
    3. Strategic & Safety Impact
    """
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"model": "deepseek/deepseek-r1-distill-llama-70b:free", "messages": [{"role": "user", "content": query}]}, timeout=25)
        return r.json()["choices"][0]["message"]["content"]
    except: return "Deep Analysis Unavailable. Manual Audit Required."

def get_dynamic_specs(prompt):
    query = f"Provide technical data for: {prompt}. Return a JSON list of 3 variations with keys: Brand, Country, Type, Material, Strength."
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": query}]}, timeout=15)
        text = r.json()["choices"][0]["message"]["content"]
        # Parsing JSON from the AI response
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])
    except:
        return [
            {"Brand": "Global Spec", "Country": "Germany", "Type": "High Performance", "Material": "Carbon Fiber", "Strength": "Industrial Grade"},
            {"Brand": "Bharat Tech", "Country": "India", "Type": "Luxury Bespoke", "Material": "Leatherette", "Strength": "High Durability"},
            {"Brand": "Nippon Parts", "Country": "Japan", "Type": "Precision", "Material": "Alloy Steel", "Strength": "Military Grade"}
        ]

# =====================================================================
# 🎨 MAIN UI
# =====================================================================
MODELS = {
    "Realistic Vision V6 (Automotive)": "SG161222/Realistic_Vision_V6.0_B1_noVAE",
    "Flux.1-Schnell (Ultra Fast)": "black-forest-labs/FLUX.1-schnell",
    "Automotive 3D (Refined)": "stabilityai/stable-diffusion-3-medium-diffusers",
}

model_choice = st.selectbox("Select Model Engine", list(MODELS.keys()))
prompt = st.text_area("CEO Engineering Prompt / RCA Topic", placeholder="Enter technical failure topic or automotive part name...")

col_btn1, col_btn2 = st.columns(2)

# --- 📸 ANALYSIS SYSTEM ---
if col_btn1.button("🔍 Run Strategic RCA & Market Analysis"):
    if not prompt: st.error("Please enter a technical topic.")
    else:
        st.markdown("---")
        with st.spinner("Executing CEO-Level Root Cause Analysis..."):
            rca_intel = get_ceo_rca_analysis(prompt)
            dynamic_data = get_dynamic_specs(prompt)
            market_data = get_serp_images(f"{prompt} 2026 industrial reference")
            
            # AI Split Comparison Image
            concept_prompt = f"3-way split comparison. Automotive technical design. {prompt}. Cinematic studio lighting. 8k."
            out_ai = hf_router_generate_image("black-forest-labs/FLUX.1-schnell", concept_prompt, width=1024, height=512)

            # 1. RCA Results
            st.markdown("<div class='ui-box rca-box'>", unsafe_allow_html=True)
            st.markdown("<h2 style='color:#ffffff !important; border-bottom: 1px solid #333;'>STRATEGIC ROOT CAUSE ANALYSIS</h2>", unsafe_allow_html=True)
            st.markdown(rca_intel)
            st.markdown("</div>", unsafe_allow_html=True)

            # 2. AI Visuals
            if out_ai and out_ai["type"] == "image":
                st.image(out_ai["data"], caption="AI Concept Design Matrix (Contextual Reference)", use_column_width=True)

            # 3. Market Matrix (Dynamic Metadata Boxes)
            st.markdown("<div class='ui-box'>", unsafe_allow_html=True)
            st.subheader("🔍 Real-World Reference & Component Markings")
            cols = st.columns(3)
            for i, col in enumerate(cols):
                with col:
                    if i < len(dynamic_data):
                        entry = dynamic_data[i]
                        st.markdown(f"<div class='car-card'><div class='label-header'>{entry.get('Brand','N/A')}</div>", unsafe_allow_html=True)
                        if i < len(market_data):
                            st.image(market_data[i]['thumbnail'], use_column_width=True)
                            st.link_button("View Intelligence 🔗", market_data[i]['link'], use_container_width=True)
                        
                        for key in ["Country", "Type", "Material", "Strength"]:
                            st.markdown(f"<div class='meta-label'>{key}</div><div class='meta-value'>{entry.get(key, 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 FINAL RENDER SYSTEM ---
if col_btn2.button("🚀 Finalize Engineering Render"):
    if not prompt: st.error("Please enter a prompt.")
    else:
        st.markdown("---")
        with st.spinner("Rendering High-Resolution Output..."):
            res = hf_router_generate_image(MODELS[model_choice], prompt)
            if res and res["type"] == "image":
                update_usage(st.session_state.current_user)
                st.image(res["data"], caption="Final Rendered Output", use_column_width=True)
                buf = io.BytesIO()
                res["data"].save(buf, format="PNG")
                st.download_button("💾 Download PNG", buf.getvalue(), "render_output.png", "image/png")

# --- DYNAMIC FOOTER RESOURCES ---
if prompt:
    st.markdown("---")
    st.subheader(f"🌐 Intelligence Hub: {prompt[:40]}...")
    dynamic_queries = [
        {"type": "YouTube", "label": "Latest Trends", "query": f"{prompt} 2026 design trends"},
        {"type": "Market", "label": "Price Comparison", "query": f"best {prompt} price india 2026"},
        {"type": "Engineering", "label": "Material Science", "query": f"{prompt} technical material science"},
        {"type": "Global", "label": "Strategic Brands", "query": f"top global competitors for {prompt}"}
    ]
    res_cols = st.columns(4)
    for i, res in enumerate(dynamic_queries):
        search_url = f"https://www.youtube.com/results?search_query={res['query'].replace(' ', '+')}" if res["type"] == "YouTube" else f"https://www.google.com/search?q={res['query'].replace(' ', '+')}"
        res_cols[i].link_button(f"🔗 {res['label']}", search_url, use_container_width=True)
