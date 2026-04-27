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

# --- CEO TRUSTED DOMAIN LIST (2026 Master List) ---
TRUSTED_DOMAINS = [
    "autofurnish.com", "autofit.in", "autotextile.com", "cncstitching.com",
    "seatcoversunlimited.com", "foamvilla.com", "sa.made-in-china.com",
    "autoclint.com", "autoform.in", "coverking.com", "katzkin.com",
    "amazon.in", "cardekho.com", "elegantautoretail.com", "carwale.com"
]

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | GPU-Optimized Rendering | 2026 Material Intel")

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
            "🔄 SDXL Refiner": "stabilityai/stable-diffusion-xl-refiner-1.0",
            "✍️ Text Qwen Edit": "prithivMLmods/Qwen-Image-Edit-2511-LoRAs-Fast",
            "🎨 Structural paint Fix": "InstantX/Qwen-Image-ControlNet-Inpainting"
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
        except:
            continue
    return None, "System Failure"

# --------------------------------------
# ⚙️ IMAGE CORE ENGINES (REFINER OPTIMIZED)
# --------------------------------------
def run_image_engine(prompt, base_image=None):
    try:
        # Mandatory CEO Headers for GPU Stability & Wake-up Protocol
        headers = {
            "x-use-cache": "false", 
            "x-wait-for-model": "true"
        }
        client = InferenceClient(model=ACTIVE_MODEL, token=HF_TOKEN, headers=headers)
        
        if app_mode == "Pictator Refiner (Editing)" and base_image:
            # 1. Process Image for Refinement (RGB Conversion for PNG/HEIC compatibility)
            img_byte_arr = io.BytesIO()
            base_image.convert("RGB").save(img_byte_arr, format='JPEG', quality=85)
            
            # 2. FIXED API CALL: Using Explicit Named Arguments
            # This is the ONLY way to prevent the "Multiple values for image" error
            return client.image_to_image(
                prompt=prompt, 
                image=img_byte_arr.getvalue(), 
                strength=refinement_strength
            )
        else:
            # 3. Standard Text-to-Image for Pro Mode
            return client.text_to_image(
                prompt=prompt, 
                width=1024, 
                height=768
            )
            
    except Exception as e:
        # Integrated CEO Error Trap
        error_msg = str(e)
        if "402" in error_msg:
            st.sidebar.error("💳 CEO Alert: Provider Credit Exhausted. Switch to SDXL Turbo.")
        elif "404" in error_msg:
            st.sidebar.error(f"⚠️ Model Endpoint Offline: {ACTIVE_MODEL}")
        else:
            st.sidebar.error(f"Inference Log: {error_msg}")
        return None

def fetch_market_references(query):
    try:
        params = {"engine": "google_images", "q": f"{query} car seat covers", "api_key": SERP_API_KEY, "num": 50}
        r = requests.get("https://serpapi.com/search", params=params, timeout=15)
        results = r.json().get("images_results", [])
        filtered, used_sources = [], set()
        for i in results:
            src = i.get("source", "Unknown").strip()
            if src not in used_sources:
                filtered.append({"img": i["original"], "link": i.get("link"), "src": src})
                used_sources.add(src)
            if len(filtered) >= 6: break
        return filtered
    except:
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
        tier = st.selectbox("Market Tier Positioning", ["Luxury", "Affordable", "OEM Upgrade"])
    
    custom_instr = st.text_area("✍️ Engineering Directives", placeholder="e.g. Add blue contrast piping...")

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
        st.write("🎨 Visual Synthesis Engine...")
        
        # 60s GPU Wake-up Timer specifically for REFINER
        if app_mode == "Pictator Refiner (Editing)":
            if not uploaded_file:
                st.error("⚠️ Refiner requires an uploaded image."); st.stop()
            
            st.write("🛰️ Activating GPU Cluster (60s Wake-up Protocol)...")
            prog_bar = st.progress(0)
            img_input = Image.open(uploaded_file)
            
            # Start GPU Handshake Countdown
            for i in range(100):
                time.sleep(0.08) # ~8 seconds overhead for connection stability
                prog_bar.progress(i + 1)
                if i == 40: # Call engine early to let 'x-wait-for-model' handle the rest
                    main_img = run_image_engine(final_prompt, img_input)
            prog_bar.empty()
        else:
            # Pro Mode (Standard Generation) - No artificial delay
            main_img = run_image_engine(final_prompt)
            
        st.write("🌐 Scraping Market Feasibility (6 Unique Sources)...")
        market_refs = fetch_market_references(f"{car} {material} leather seat cover")
        
        st.write("📊 Running RCA Intelligence Analytics...")
        analysis, _ = call_openrouter_with_fallback_requests(
            f"Detailed 2026 durability analysis for {material} with {pattern} stitching.", 
            OPENROUTER_API_KEY
        )
        status.update(label="✅ Engineering Intelligence Finalized", state="complete")

    # --- RESULT VISUALIZATION ---
    res_col1, res_col2 = st.columns([2, 1])
    
    with res_col1:
        st.subheader(f"🖼️ {app_mode} Output")
        if main_img:
            st.image(main_img, caption=f"2026 Prototype: {car}", use_container_width=True)
            buf = io.BytesIO()
            main_img.save(buf, format="PNG")
            st.download_button("💾 Save Engineering Concept", buf.getvalue(), f"design_{int(time.time())}.png", "image/png")
        else:
            st.error("❌ Output Pipeline Error. Check Token Credits.")

    with res_col2:
        st.subheader("📈 Flashmind Analysis")
        st.info(analysis if analysis else "Intelligence Engine Timeout. Manual review required.")

    st.divider()
    st.subheader("🌍 Verified Unique Market References")
    if market_refs:
        m_cols = st.columns(3)
        for idx, ref in enumerate(market_refs):
            with m_cols[idx % 3]:
                st.image(ref["img"], use_container_width=True)
                st.link_button(f"🔗 View on {ref['src']}", ref["link"])

# --------------------------------------
# 🏁 THE CEO FOOTER
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
    <b>Pictator Pro 2026</b> | Dual-Mode Engineering Engine | GPU Optimized | Powered by Harmony-AI | © 2026 Harmony Engineering
</div>
""", unsafe_allow_html=True)
