import io
import json
import requests
import streamlit as st
import re
import time
import threading
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------
# 🔧 PAGE CONFIG + CYBER-DARK THEME
# --------------------------------------
st.set_page_config(
    page_title="Pictator Pro: Parallel Engine",
    page_icon="🏎️",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;700&display=swap');
    
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #00eaff !important; text-transform: uppercase; letter-spacing: 2px; }
    
    .car-card { border: 1px solid #333333; border-radius: 4px; padding: 15px; margin-bottom: 15px; background: #0a0a0a; box-shadow: 0 4px 15px rgba(0,234,255,0.05); transition: transform 0.3s ease;}
    .car-card:hover { transform: translateY(-3px); border-color: #00eaff; }
    
    .label-header { color: #ffffff; font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 18px; border-bottom: 1px solid #222; margin-bottom: 10px; padding-bottom: 5px;}
    .meta-label { color: #00eaff; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-top: 8px; letter-spacing: 1px;}
    .meta-value { color: #ffffff; font-family: 'Inter', sans-serif; font-size: 14px; margin-bottom: 8px; }
    
    .ui-box { border: 1px solid #00eaff; border-radius: 8px; padding: 25px; background: #050505; margin-top: 20px; }
    .rca-box { border-left: 4px solid #ff00ff; padding: 20px; background: #0a0a0a; margin-bottom: 25px; font-family: 'Inter', sans-serif; line-height: 1.6; color: #eee; }
    
    .stButton>button { 
        background: linear-gradient(90deg, #00eaff, #0072ff); 
        color: #000000 !important; font-weight: 800; border: none; border-radius: 4px; width: 100%; height: 50px; text-transform: uppercase;
    }
    .stTextArea textarea { background-color: #0a0a0a !important; color: #ffffff !important; border: 1px solid #333333 !important; font-family: 'Inter', sans-serif; }
    
    .stLinkButton > a { background-color: #ffffff !important; color: #000000 !important; font-weight: 700 !important; border-radius: 2px !important; }
    </style>
    <h1 style='text-align:center;'>🏎️ Pictator Pro – CEO Engineering Suite</h1>
    <h3 style='text-align:center;color:#888888;font-size:16px;'>Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel</h3>
    <hr style='border:1px solid #222'>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# 🔵 PERSISTENT USAGE TRACKER
# =====================================================================
if "count" not in st.session_state:
    st.session_state.count = 0

st.sidebar.title("🔐 Control Panel")
st.sidebar.metric("Analysis Generations", st.session_state.count)
st.sidebar.markdown("---")

# =====================================================================
# 🧵 THREAD-SAFE RESULT CONTAINER
# =====================================================================
class AnalysisResults:
    def __init__(self):
        self.rca_intel = "[❌ Failed to load RCA]"
        self.specs_raw = ""
        self.market_photos = []
        self.ai_concept = None

# =====================================================================
# ⚡ ENGINES
# =====================================================================
OPENROUTER_API_KEY = "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"
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "") 
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

ANALYSIS_FALLBACK_MODELS = ["openai/gpt-oss-20b:free", "meta-llama/llama-3.2-3b-instruct:free", "deepseek/deepseek-r1-distill-llama-70b:free"]

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in ANALYSIS_FALLBACK_MODELS:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, 
                              json={"model": model, "messages": [{"role": "user", "content": prompt}]}, timeout=60)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"].strip()
        except: continue
    return ""

def hf_gen_image(prompt, width=1024, height=512):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        resp = requests.post(url, headers=headers, json={"inputs": prompt, "parameters": {"width": width, "height": height}}, timeout=90)
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except: return None

# =====================================================================
# 🛰️ PARALLEL FETCH FUNCTIONS
# =====================================================================
def thread_rca(res_obj, prompt):
    res_obj.rca_intel = call_openrouter(f"Perform CEO Root Cause Analysis for: {prompt}. Focus on Physics and 2026 industry evidence.")

def thread_meta(res_obj, prompt):
    res_obj.specs_raw = call_openrouter(f"Return ONLY a JSON list of 3 automotive variations for '{prompt}'. Keys: Brand, Country, Type, Material, Strength.")

def thread_assets(res_obj, prompt):
    try:
        r = requests.get("https://serpapi.com/search", params={"engine": "google_images", "q": f"{prompt} 2026 industrial", "api_key": SERP_API_KEY}, timeout=15)
        res_obj.market_photos = r.json().get("images_results", [])[:3]
    except: res_obj.market_photos = []
    res_obj.ai_concept = hf_gen_image(f"Automotive engineering split view, {prompt}, 8k")

# =====================================================================
# 🎨 MAIN UI
# =====================================================================
prompt = st.text_area("CEO Engineering Prompt / RCA Topic", placeholder="Enter technical topic for strategic analysis...")

col_btn1, col_btn2 = st.columns(2)

if col_btn1.button("🚀 EXECUTE INDEPENDENT ENGINES"):
    if not prompt: st.error("Prompt required.")
    else:
        results = AnalysisResults()
        st.markdown("---")
        
        with st.status("Omnicore Independent Engines Loading...", expanded=True) as status:
            t1 = threading.Thread(target=thread_rca, args=(results, prompt))
            t2 = threading.Thread(target=thread_meta, args=(results, prompt))
            t3 = threading.Thread(target=thread_assets, args=(results, prompt))
            
            st.write("🛰️ Dispatching OpenRouter Fallback Logic...")
            t1.start(); t2.start()
            st.write("📷 Engaging Hugging Face Parallel Stream...")
            t3.start()
            
            t1.join(); st.write("✅ RCA Text Engine Synchronized.")
            t2.join(); st.write("✅ Component Metadata Mapped.")
            t3.join(); st.write("✅ Visual Matrices Ready.")
            status.update(label="Strategic Data Pack Complete!", state="complete")

        # --- RENDER RCA ---
        st.markdown("<div class='rca-box'><h3>STRATEGIC ROOT CAUSE ANALYSIS</h3>" + results.rca_intel + "</div>", unsafe_allow_html=True)
        
        # --- RENDER AI VISUAL ---
        if results.ai_concept: st.image(results.ai_concept, caption="AI Concept Design Matrix", use_column_width=True)

        # --- RENDER TECH BOXES ---
        st.markdown("<div class='ui-box'><h3>🔍 Technical Markings & References</h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        try:
            match = re.search(r'\[.*\]', results.specs_raw, re.DOTALL)
            specs = json.loads(match.group()) if match else []
        except: specs = [{"Brand": "Global Spec", "Country": "Germany", "Type": "Performance", "Material": "Carbon", "Strength": "Industrial"}]

        for i, col in enumerate(cols):
            with col:
                data = specs[i] if i < len(specs) else specs[0]
                st.markdown(f"<div class='car-card'><div class='label-header'>{data.get('Brand','N/A')}</div>", unsafe_allow_html=True)
                if i < len(results.market_photos):
                    st.image(results.market_photos[i]['thumbnail'], use_column_width=True)
                    st.link_button("View Source 🔗", results.market_photos[i]['link'], use_container_width=True)
                for k in ["Country", "Type", "Material", "Strength"]:
                    st.markdown(f"<div class='meta-label'>{k}</div><div class='meta-value'>{data.get(k,'N/A')}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

if col_btn2.button("📷 HIGH-RES RENDER"):
    if not prompt: st.error("Enter a prompt.")
    else:
        with st.spinner("Generating 3D Visual..."):
            render = hf_gen_image(f"Professional automotive 3D render, {prompt}, cinematic, 8k", width=1024, height=1024)
            if render:
                st.session_state.count += 1
                st.image(render, use_column_width=True)
                st.rerun()

# DYNAMIC FOOTER
if prompt:
    st.markdown("---")
    fcols = st.columns(4)
    links = [("YouTube Trends", f"https://www.youtube.com/results?search_query={prompt.replace(' ','+')}+2026"),
             ("Material Science", f"https://www.google.com/search?q={prompt.replace(' ','+')}+technical+data"),
             ("Market Prices", f"https://www.google.com/search?q={prompt.replace(' ','+')}+price+india"),
             ("Global Standards", f"https://www.google.com/search?q={prompt.replace(' ','+')}+AIS+safety")]
    for i, (label, url) in enumerate(links): fcols[i].link_button(label, url, use_container_width=True)
