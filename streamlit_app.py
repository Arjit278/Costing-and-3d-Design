import io
import requests
import streamlit as st
import json
import time
import re
from PIL import Image
from huggingface_hub import InferenceClient

# --------------------------------------
# 🔧 PAGE CONFIG & API
# --------------------------------------
st.set_page_config(page_title="Pictator Pro 2026", page_icon="🏎️", layout="wide")

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

TRUSTED_DOMAINS = [
    "autofurnish.com", "autofit.in", "autotextile.com", "cncstitching.com",
    "seatcoversunlimited.com", "foamvilla.com", "sa.made-in-china.com",
    "autoclint.com", "autoform.in", "coverking.com", "katzkin.com",
    "amazon.in", "cardekho.com"
]

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# 🔐 AUTHENTICATION
# --------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.title("🔐 Access Panel")
    if not st.session_state.authenticated:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Harmony" and pwd == "Harmony_Pictator123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    else:
        st.success("🟢 Logged in as Harmony")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.stop()

# --------------------------------------
# ⚡ MODE TOGGLE & STABLE MODEL STACK
# --------------------------------------
with st.sidebar:
    st.divider()
    app_mode = st.radio("🚀 Select Suite Mode", ["Pictator Pro (Base)", "Pictator Refiner (Edit)"], key="mode_sel_final")
    
    if app_mode == "Pictator Pro (Base)":
        BASE_MODELS = {
            "⚡ SDXL Turbo (High Speed)": "stabilityai/sdxl-turbo",
            "✨ SDXL Base 1.0": "stabilityai/stable-diffusion-xl-base-1.0",
            "🎨 Realistic Vision V6": "SG161222/Realistic_Vision_V6.0_B1_noVAE"
        }
        selected_model = st.selectbox("Choose AI Model", list(BASE_MODELS.keys()))
        ACTIVE_MODEL = BASE_MODELS[selected_model]
        uploaded_file = None 
    else:
        EDIT_MODELS = {
            "🔄 SDXL Refiner": "stabilityai/stable-diffusion-xl-refiner-1.0",
            "✍️ Text Command Edit": "timbrooks/instruct-pix2pix",
            "🎨 Pattern Fix": "lllyasviel/sd-controlnet-canny"
        }
        selected_model = st.selectbox("Choose Refinement Engine", list(EDIT_MODELS.keys()))
        ACTIVE_MODEL = EDIT_MODELS[selected_model]
        uploaded_file = st.file_uploader("Upload Base Design", type=["png", "jpg", "jpeg"])
        refinement_strength = st.slider("Refinement Strength", 0.1, 0.9, 0.5)

# --------------------------------------
# ⚡ FLASHMIND ENGINE (Your Working Fallback)
# --------------------------------------
ANALYSIS_FALLBACK_MODELS = [
    "qwen/qwen-3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct",
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
                        {"role": "system", "content": "You are an automotive engineering expert."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                },
                timeout=60
            )
            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if content:
                    return content.strip(), "OK"
            elif r.status_code == 429:
                time.sleep(2)
        except:
            continue
    return None, "All models failed"

def safe_json_extract(text):
    try:
        text = str(text)
        return json.loads(text)
    except:
        pass
    try:
        match = re.search(r"\[\s*{.*?}\s*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return []

# --------------------------------------
# ⚙️ IMAGE ENGINES
# --------------------------------------
def run_image_engine(prompt, base_image=None):
    try:
        headers = {"x-use-cache": "false"}
        client = InferenceClient(model=ACTIVE_MODEL, token=HF_TOKEN, headers=headers)
        if app_mode == "Pictator Refiner (Edit)" and base_image:
            img_byte_arr = io.BytesIO()
            base_image = base_image.convert("RGB")
            base_image.save(img_byte_arr, format='JPEG')
            return client.image_to_image(prompt=prompt, image=img_byte_arr.getvalue(), strength=refinement_strength)
        else:
            return client.text_to_image(prompt=prompt, width=1024, height=768)
    except Exception as e:
        if "402" in str(e):
            st.error("💳 CEO Error: Provider Credit Exhausted. Switching to 'SDXL Turbo' is recommended.")
        st.sidebar.error(f"Engine Detail: {e}")
        return None

def fetch_market_references(query):
    try:
        params = {"engine": "google_images", "q": f"{query} luxury car seat cover", "api_key": SERP_API_KEY, "num": 40}
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        filtered, used = [], set()
        for i in results:
            src = i.get("source", "").strip()
            if src not in used and any(td in i.get("link", "").lower() for td in TRUSTED_DOMAINS):
                filtered.append({"img": i["original"], "link": i.get("link"), "src": src})
                used.add(src)
            if len(filtered) >= 6: break
        return filtered
    except: return []

# --------------------------------------
# 🎯 SMART CONFIGURATOR
# --------------------------------------
with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
    colA, colB, colC = st.columns(3)
    with colA:
        car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Custom/Other"])
        pattern = st.selectbox("Stitching", ["Ultra-Quilt Diamond", "Hex-Cell", "Puff", "Minimalist Flat"])
    with colB:
        material = st.selectbox("Material", ["1200 GSM Nappa", "Cotton", "Synthetic Leather", "Carbon Fiber Leather"])
        colors = st.text_input("Colorway", value="Tan & Charcoal")
    with colC:
        lighting = st.selectbox("Lighting", ["Studio", "Blueprint", "Cinematic Showroom"])
        market = st.selectbox("Market Tier", ["Luxury", "Affordable", "Sports", "OEM Upgrade"])
    custom_instruction = st.text_area("✍️ Engineering Instructions", placeholder="Add blue contrast stitching details...")

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE ENGINEERING SUITE", key="exec_btn_master"):
    final_prompt = (
        f"Professional automotive interior photography, {car} custom seat covers, "
        f"{pattern} pattern, premium {material}, {colors} theme, "
        f"{custom_instruction}, {lighting} lighting, 8k ultra-realistic."
    )
    
    with st.status("Processing Virtual Prototype...") as status:
        main_img = None
        if app_mode == "Pictator Refiner (Edit)":
            if uploaded_file:
                input_img = Image.open(uploaded_file)
                main_img = run_image_engine(final_prompt, input_img)
            else:
                st.error("⚠️ Please upload an image to use Refiner."); st.stop()
        else:
            main_img = run_image_engine(final_prompt)
            
        st.write("🌐 Verifying Unique Market Links...")
        market_refs = fetch_market_references(f"{car} {material} seat cover")
        
        st.write("📊 Finalizing RCA Analysis...")
        # CALLING YOUR CUSTOM OPENROUTER FUNCTION
        analysis, status_code = call_openrouter_with_fallback_requests(
            f"Briefly analyze durability and 2026 trends for {material} with {pattern} stitching.",
            OPENROUTER_API_KEY
        )
        status.update(label="✅ Engineering Complete", state="complete")

    # Display Results
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader(f"🖼️ {app_mode} Output")
        if main_img:
            st.image(main_img, use_container_width=True)
            buf = io.BytesIO(); main_img.save(buf, format="PNG")
            st.download_button("💾 Save Prototype", buf.getvalue(), f"design_{int(time.time())}.png")
        else:
            st.error("❌ Output Failed. Check credits or rotate HF token.")

    with col_right:
        st.subheader("📈 Flashmind Analysis")
        if analysis:
            st.info(analysis)
        else:
            st.warning("Intelligence Engine timed out. Manual review required.")

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
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0e1117; color: #555; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #333; z-index: 100; }
</style>
<div class="footer">
    <b>Pictator Pro 2026</b> | Dual-Mode Engineering Engine | Zero Data Retention Protocol | © 2026 Harmony Engineering
</div>
""", unsafe_allow_html=True)
