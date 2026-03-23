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
    
    /* Global Styling */
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #00eaff !important; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Technical Metadata Cards */
    .car-card { border: 1px solid #333333; border-radius: 4px; padding: 15px; margin-bottom: 15px; background: #0a0a0a; box-shadow: 0 4px 15px rgba(0,234,255,0.05); transition: transform 0.3s ease;}
    .car-card:hover { transform: translateY(-3px); border-color: #00eaff; }
    
    .label-header { color: #ffffff; font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 18px; border-bottom: 1px solid #222; margin-bottom: 10px; padding-bottom: 5px;}
    .meta-label { color: #00eaff; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-top: 8px; letter-spacing: 1px;}
    .meta-value { color: #ffffff; font-family: 'Inter', sans-serif; font-size: 14px; margin-bottom: 8px; }
    
    /* RCA & UI Boxes */
    .ui-box { border: 1px solid #00eaff; border-radius: 8px; padding: 25px; background: #050505; margin-top: 20px; }
    .rca-box { border-left: 4px solid #ff00ff; padding: 20px; background: #0a0a0a; margin-bottom: 25px; font-family: 'Inter', sans-serif; line-height: 1.6; color: #eee; }
    
    /* Buttons */
    .stButton>button { 
        background: linear-gradient(90deg, #00eaff, #0072ff); 
        color: #000000 !important; font-weight: 800; border: none; border-radius: 4px; width: 100%; height: 50px; text-transform: uppercase;
    }
    .stTextArea textarea { background-color: #0a0a0a !important; color: #ffffff !important; border: 1px solid #333333 !important; font-family: 'Inter', sans-serif; }
    
    /* Link Styling */
    .stLinkButton > a { background-color: #ffffff !important; color: #000000 !important; font-weight: 700 !important; border-radius: 2px !important; border: none !important;}
    </style>
    <h1 style='text-align:center;'>🏎️ Pictator Pro – CEO Engineering Suite</h1>
    <h3 style='text-align:center;color:#888888;font-size:16px;'>Board-Level RCA | Dynamic Design | 2026 Material Intelligence</h3>
    <hr style='border:1px solid #222'>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# 🔵 PERSISTENT USAGE TRACKER
# =====================================================================
@st.cache_resource
def init_store(): return {"count": 0}
usage = init_store()

# =====================================================================
# ⚡ FLASHMIND ENGINE (OpenRouter Fallback Chain)
# =====================================================================
ANALYSIS_FALLBACK_MODELS = [
    "openai/gpt-oss-20b:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "x-ai/grok-4.1-fast:free",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "") 
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

def call_openrouter_fallback(prompt_text: str):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in ANALYSIS_FALLBACK_MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a senior automotive CEO and technical analyst. Provide structured, evidence-based data."},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.2
        }
        try:
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=45)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            time.sleep(1)
        except:
            continue
    return "[❌ Error: Technical Engines Timed Out. Verify Connection.]"

# =====================================================================
# 🛰️ HELPER ENGINES
# =====================================================================
def get_serp_images(query):
    try:
        resp = requests.get("https://serpapi.com/search", 
                            params={"engine": "google_images", "q": query, "api_key": SERP_API_KEY}, 
                            timeout=15)
        return resp.json().get("images_results", [])[:3]
    except: return []

def hf_gen_image(prompt_text, width=1024, height=512):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        resp = requests.post(url, headers=headers, json={"inputs": prompt_text, "parameters": {"width": width, "height": height}}, timeout=60)
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except: return None

# --------------------------------------
# SIDEBAR (LEFT COLUMN COUNTER)
# --------------------------------------
st.sidebar.title("🔐 Control Panel")
st.sidebar.metric("Analysis Generations", usage["count"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Last Session Update: {datetime.now().strftime('%H:%M:%S')}")

# --------------------------------------
# 🎨 MAIN UI EXECUTION
# --------------------------------------
prompt = st.text_area("CEO Engineering Prompt / RCA Topic", placeholder="Describe technical failure or design specs (e.g., 'Thermal stress in alloy wheels')...")

col_btn1, col_btn2 = st.columns(2)

if col_btn1.button("🚀 EXECUTE STRATEGIC ANALYSIS"):
    if not prompt: st.error("Please enter a prompt.")
    else:
        st.markdown("---")
        with st.spinner("Processing CEO-Level Intelligence Chain (Chemistry/Physics/Business)..."):
            # RCA and Metadata logic
            rca_query = f"Perform CEO-level Root Cause Analysis for: {prompt}. Focus on Physics, Chemistry, and 2026 Industry standards."
            rca_intel = call_openrouter_fallback(rca_query)
            
            meta_query = f"Return ONLY a JSON list of 3 automotive variations for '{prompt}'. Use keys: Brand, Country, Type, Material, Strength."
            specs_raw = call_openrouter_fallback(meta_query)
            
            # Asset logic
            market_photos = get_serp_images(f"{prompt} 2026 industrial reference")
            ai_concept = hf_gen_image(f"3-way automotive engineering split view, technical diagram, {prompt}, studio lighting, 8k")

            st.markdown("<div class='rca-box'><h3>STRATEGIC ROOT CAUSE ANALYSIS</h3>" + rca_intel + "</div>", unsafe_allow_html=True)
            if ai_concept: st.image(ai_concept, caption="AI Concept Design Matrix", use_column_width=True)

            st.markdown("<div class='ui-box'><h3>🔍 Technical Markings & Real-World References</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            
            try:
                match = re.search(r'\[.*\]', specs_raw, re.DOTALL)
                specs = json.loads(match.group()) if match else []
            except: 
                specs = [
                    {"Brand": "Global Spec", "Country": "Germany", "Type": "Performance", "Material": "Carbon Fiber", "Strength": "Industrial"},
                    {"Brand": "Bharat Tech", "Country": "India", "Type": "Luxury", "Material": "Nappa Leather", "Strength": "High Durability"},
                    {"Brand": "Nippon Parts", "Country": "Japan", "Type": "Precision", "Material": "Alloy Steel", "Strength": "Military Grade"}
                ]

            for i, col in enumerate(cols):
                with col:
                    data = specs[i] if i < len(specs) else specs[0]
                    st.markdown(f"<div class='car-card'><div class='label-header'>{data.get('Brand','N/A')}</div>", unsafe_allow_html=True)
                    if i < len(market_photos):
                        st.image(market_photos[i]['thumbnail'], use_column_width=True)
                        st.link_button("View Source 🔗", market_photos[i]['link'], use_container_width=True)
                    
                    for k in ["Country", "Type", "Material", "Strength"]:
                        st.markdown(f"<div class='meta-label'>{k}</div><div class='meta-value'>{data.get(k,'N/A')}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

if col_btn2.button("📷 HIGH-RES 3D RENDER"):
    if not prompt: st.error("Enter a prompt.")
    else:
        with st.spinner("Generating 3D Board-Ready Visual..."):
            render = hf_gen_image(f"Automotive 3D render, {prompt}, cinematic, 8k", width=1024, height=1024)
            if render:
                usage["count"] += 1
                st.image(render, caption="Final Engineering Render", use_column_width=True)
                st.rerun() 

# --- DYNAMIC FOOTER ---
if prompt:
    st.markdown("---")
    st.subheader(f"🌐 Intelligence Hub: {prompt[:40]}")
    fcols = st.columns(4)
    links = [
        ("YouTube Trends", f"https://www.youtube.com/results?search_query={prompt.replace(' ','+')}+2026+review"),
        ("Material Specs", f"https://www.google.com/search?q={prompt.replace(' ','+')}+technical+data+sheet+physics"),
        ("Market Costs", f"https://www.google.com/search?q={prompt.replace(' ','+')}+price+india+2026"),
        ("Global Standards", f"https://www.google.com/search?q={prompt.replace(' ','+')}+safety+certification+AIS")
    ]
    for i, (label, url) in enumerate(links):
        fcols[i].link_button(label, url, use_container_width=True)
