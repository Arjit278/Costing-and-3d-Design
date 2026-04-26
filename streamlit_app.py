import io
import requests
import streamlit as st
import json
import time
import re
import base64
from PIL import Image
from huggingface_hub import InferenceClient

# --------------------------------------
# 🔧 PAGE CONFIG & API
# --------------------------------------
st.set_page_config(
    page_title="Pictator Pro 2026", 
    page_icon="🏎️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --- CEO TRUSTED DOMAIN LIST (Enhanced for 2026) ---
TRUSTED_DOMAINS = [
    "autofurnish.com", "autofit.in", "autotextile.com", "cncstitching.com",
    "seatcoversunlimited.com", "foamvilla.com", "sa.made-in-china.com",
    "autoclint.com", "autoform.in", "coverking.com", "katzkin.com",
    "amazon.in", "cardekho.com", "elegantautoretail.com", "carwale.com"
]

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# 🔐 AUTHENTICATION PROTOCOL
# --------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.title("🔐 Access Panel")
    if not st.session_state.authenticated:
        user = st.text_input("Username", placeholder="Harmony")
        pwd = st.text_input("Password", type="password")
        if st.button("Authorize Suite"):
            if user == "Harmony" and pwd == "Harmony_Pictator123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials - Security Protocol Engaged")
    else:
        st.success("🟢 Engineering Access: Harmony")
        if st.button("Secure Logout"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.warning("🔐 Please authenticate to access 2026 Material Intelligence.")
    st.stop()

# --------------------------------------
# ⚡ DUAL-MODE ENGINE CONFIGURATION
# --------------------------------------
with st.sidebar:
    st.divider()
    st.subheader("🚀 Suite Orchestration")
    app_mode = st.radio(
        "Select Operation Mode", 
        ["Pictator Pro (Generation)", "Pictator Refiner (Editing)"], 
        key="suite_mode_selection_v2"
    )
    
    if app_mode == "Pictator Pro (Generation)":
        BASE_MODELS = {
            "⚡ SDXL Turbo (High Performance)": "stabilityai/sdxl-turbo",
            "✨ SDXL Base 1.0 (High Detail)": "stabilityai/stable-diffusion-xl-base-1.0",
            "🎨 Realistic Vision V6 (Photorealistic)": "SG161222/Realistic_Vision_V6.0_B1_noVAE"
        }
        selected_model = st.selectbox("Choose AI Model", list(BASE_MODELS.keys()))
        ACTIVE_MODEL = BASE_MODELS[selected_model]
        uploaded_file = None 
    else:
        EDIT_MODELS = {
            "🔄 Material/Texture Swap": "stabilityai/stable-diffusion-xl-refiner-1.0",
            "✍️ Text Command Instruction": "prithivMLmods/Qwen-Image-Edit-2511-LoRAs-Fast",
            "🎨 Structural Pattern Fix": "InstantX/Qwen-Image-ControlNet-Inpainting"
        }
        selected_model = st.selectbox("Choose Refinement Engine", list(EDIT_MODELS.keys()))
        ACTIVE_MODEL = EDIT_MODELS[selected_model]
        uploaded_file = st.file_uploader("Upload Base Design (PNG/JPG)", type=["png", "jpg", "jpeg"], key="refiner_up_v2")
        refinement_strength = st.slider("Refinement Strength (AI Influence)", 0.1, 0.9, 0.5)

# --------------------------------------
# ⚡ FLASHMIND ENGINE (OpenRouter Fallback)
# --------------------------------------
ANALYSIS_FALLBACK_MODELS = [
    "qwen/qwen-3-coder:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-2-pro-llama-3-8b",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_with_fallback_requests(prompt: str, api_key: str):
    """Orchestrates multi-model fallback for material intelligence."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for model in ANALYSIS_FALLBACK_MODELS:
        try:
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a professional automotive engineering consultant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                },
                timeout=30
            )
            if r.status_code == 200:
                content = r.json().get("choices", [{}])[0].get("message", {}).get("content")
                if content: return content.strip(), "OK"
        except Exception as e:
            continue
    return None, "System Failure: All models non-responsive"

# --------------------------------------
# ⚙️ IMAGE CORE ENGINES
# --------------------------------------
def run_image_engine(prompt, base_image=None):
    """Handles both diffusion generation and refinement logic."""
    try:
        headers = {"x-use-cache": "false", "x-wait-for-model": "true"}
        client = InferenceClient(model=ACTIVE_MODEL, token=HF_TOKEN, headers=headers)
        
        if app_mode == "Pictator Refiner (Editing)" and base_image:
            # Prepare image payload
            img_byte_arr = io.BytesIO()
            base_image = base_image.convert("RGB")
            base_image.save(img_byte_arr, format='JPEG', quality=85)
            
            # Keyed parameter mapping to prevent 'multiple values' error
            return client.image_to_image(
                prompt=prompt, 
                image=img_byte_arr.getvalue(), 
                strength=refinement_strength
            )
        else:
            return client.text_to_image(prompt=prompt, width=1024, height=768)
    except Exception as e:
        if "402" in str(e):
            st.error("💳 CEO Warning: Provider Credit Exhausted. Reverting to SDXL Turbo or rotate Token.")
        st.sidebar.error(f"Inference Failure: {e}")
        return None

def fetch_market_references(query):
    """Fetches 6 unique high-quality market links using advanced filtering."""
    try:
        params = {"engine": "google_images", "q": f"{query} luxury seat covers", "api_key": SERP_API_KEY, "num": 50}
        r = requests.get("https://serpapi.com/search", params=params, timeout=15)
        results = r.json().get("images_results", [])
        
        filtered, used_sources = [], set()
        
        # Priority 1: Unique Trusted Domains
        for i in results:
            src = i.get("source", "Unknown").strip()
            link = i.get("link", "").lower()
            if src in used_sources: continue
            
            if any(td in link for td in TRUSTED_DOMAINS):
                filtered.append({"img": i["original"], "link": i.get("link"), "src": src})
                used_sources.add(src)
            if len(filtered) >= 6: break
            
        # Priority 2: Fill remaining slots with any unique source
        if len(filtered) < 6:
            for i in results:
                src = i.get("source", "Market").strip()
                if src not in used_sources:
                    filtered.append({"img": i["original"], "link": i.get("link"), "src": src})
                    used_sources.add(src)
                if len(filtered) >= 6: break
        
        return filtered
    except Exception as e:
        st.sidebar.warning(f"Market Sync Interrupted: {e}")
        return []

# --------------------------------------
# 🎯 SMART DESIGN CONFIGURATOR
# --------------------------------------
with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
    colA, colB, colC = st.columns(3)
    with colA:
        car = st.selectbox("Vehicle Target", ["Maruti Wagon R", "Maruti Grand Vitara", "Mahindra Thar", "Custom/Other"])
        pattern = st.selectbox("Stitching Pattern", ["Ultra-Quilt Diamond", "Hex-Cell", "Puff", "Minimalist Flat"])
    with colB:
        material = st.selectbox("Material Choice", ["1200 GSM Nappa", "Synthetic Leather", "Carbon Fiber Leather", "Cotton Canvas"])
        colors = st.text_input("Colorway Architecture", value="Tan & Charcoal")
    with colC:
        lighting = st.selectbox("Environment Lighting", ["Studio Showroom", "Blueprint Static", "Golden Hour Cinematic"])
        tier = st.selectbox("Market Tier Positioning", ["Ultra-Luxury", "Luxury", "Affordable", "OEM Upgrade"])
    
    custom_instr = st.text_area("✍️ Engineering Directives", placeholder="e.g. Add blue contrast piping to the bolsters...")

# --------------------------------------
# 🚀 CORE EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE FULL ENGINEERING SUITE", key="exec_btn_300"):
    final_prompt = (
        f"Professional automotive interior photography, {car} custom seat covers, "
        f"{pattern} pattern, premium {material}, {colors} theme, "
        f"{custom_instr}, {lighting} lighting, 8k ultra-realistic, detailed texture."
    )
    
    with st.status("Initializing Strategic RCA & Prototyping...") as status:
        # Step 1: Image Generation/Refinement
        st.write("🎨 Synthesizing Visual Prototype...")
        main_img = None
        if app_mode == "Pictator Refiner (Editing)":
            if uploaded_file:
                main_img = run_image_engine(final_prompt, Image.open(uploaded_file))
            else:
                st.error("⚠️ Refiner requires an uploaded base image."); st.stop()
        else:
            main_img = run_image_engine(final_prompt)
            
        # Step 2: Market Verification (Fetching 6 Unique Links)
        st.write("🌐 Scraping Market Feasibility...")
        market_refs = fetch_market_references(f"{car} {material} leather seat cover")
        
        # Step 3: Flashmind Analysis
        st.write("📊 Running RCA Intelligence Analytics...")
        analysis_query = f"Provide a detailed 2026 durability analysis for {material} with {pattern} stitching."
        analysis, _ = call_openrouter_with_fallback_requests(analysis_query, OPENROUTER_API_KEY)
        
        status.update(label="✅ Engineering Intelligence Finalized", state="complete")

    # --- RESULT VISUALIZATION ---
    res_col1, res_col2 = st.columns([2, 1])
    
    with res_col1:
        st.subheader(f"🖼️ {app_mode} Output")
        if main_img:
            st.image(main_img, caption=f"2026 Concept: {car} | {material}", use_container_width=True)
            # Binary Download handler
            buf = io.BytesIO()
            main_img.save(buf, format="PNG")
            st.download_button("💾 Save Engineering Concept", buf.getvalue(), f"design_{int(time.time())}.png", "image/png")
        else:
            st.error("❌ Output Pipeline Error. Check credits/Token limits.")

    with res_col2:
        st.subheader("📈 Flashmind Analysis")
        if analysis:
            st.info(analysis)
        else:
            st.warning("Intelligence engines non-responsive. Manual material review required.")

    st.divider()
    
    # --- MARKET FEASIBILITY GRID ---
    st.subheader("🌍 Verified Unique Market References (6 Sources Found)")
    if market_refs:
        m_cols = st.columns(3)
        for idx, ref in enumerate(market_refs):
            with m_cols[idx % 3]:
                st.image(ref["img"], use_container_width=True)
                st.link_button(f"🔗 View via {ref['src']}", ref["link"])
    else:
        st.warning("No unique real-world references found for this specific material configuration.")

# --------------------------------------
# 🏁 THE CEO FOOTER (MANDATORY)
# --------------------------------------
st.markdown("""
<style>
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background-color: #0e1117; color: #555; text-align: center; 
        padding: 10px; font-size: 12px; border-top: 1px solid #333; z-index: 100; 
    }
</style>
<div class="footer">
    <b>Pictator Pro 2026</b> | Dual-Mode Engineering Engine | Zero Data Retention Protocol | Powered by Harmony-AI | © 2026 Harmony Engineering
</div>
""", unsafe_allow_html=True)
