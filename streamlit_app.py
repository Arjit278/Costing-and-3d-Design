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

# --- CEO TRUSTED DOMAIN LIST ---
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
# ⚡ MODE TOGGLE & MODEL STACK
# --------------------------------------
with st.sidebar:
    st.divider()
    app_mode = st.radio("🚀 Select Suite Mode", ["Pictator Pro (Base)", "Pictator Refiner (Edit)"])
    
    if app_mode == "Pictator Pro (Base)":
        BASE_MODELS = {
            "⚡ Virtual Prototype (Fastest)": "stabilityai/sdxl-turbo",
            "✨ Virtual Advanced": "stabilityai/stable-diffusion-xl-base-1.0",
            "🎨 Realistic Vision": "SG161222/Realistic_Vision_V6.0_B1_noVAE"
        }
        selected_model = st.selectbox("Choose AI Model", list(BASE_MODELS.keys()))
        ACTIVE_MODEL = BASE_MODELS[selected_model]
        uploaded_file = None 
    else:
        EDIT_MODELS = {
            "🔄 Material Swap": "stabilityai/stable-diffusion-xl-refiner-1.0",
            "🎨 Pattern Fix": "lllyasviel/sd-controlnet-canny",
            "✍️ Text Command": "timbrooks/instruct-pix2pix"
        }
        selected_model = st.selectbox("Choose Refinement Engine", list(EDIT_MODELS.keys()))
        ACTIVE_MODEL = EDIT_MODELS[selected_model]
        uploaded_file = st.file_uploader("Upload Base Design", type=["png", "jpg", "jpeg"])
        refinement_strength = st.slider("Refinement Strength", 0.1, 0.9, 0.5)

# --------------------------------------
# ⚙️ ENGINES
# --------------------------------------
def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "qwen/qwen-3-coder:free",
                "messages": [{"role": "user", "content": prompt}]
            }, timeout=15
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return "Intelligence fallback active: Manual review required for 2026 Material Compliance."

def run_image_engine(prompt, base_image=None):
    try:
        client = InferenceClient(model=ACTIVE_MODEL, token=HF_TOKEN)
        if app_mode == "Pictator Refiner (Edit)" and base_image:
            img_byte_arr = io.BytesIO()
            base_image = base_image.convert("RGB")
            base_image.save(img_byte_arr, format='JPEG', quality=95)
            return client.image_to_image(
                prompt, 
                image=img_byte_arr.getvalue(), 
                strength=refinement_strength,
                guidance_scale=7.5
            )
        else:
            return client.text_to_image(prompt, width=1024, height=768)
    except Exception as e:
        st.sidebar.error(f"Engine Detail: {e}")
        return None

def generate_image_via_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={
            "model": "google/imagen-3", # Or another available image model
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        }
    )
    # Note: OpenRouter usually returns a URL for the image
    return r.json()['choices'][0]['message']['content']
    
def fetch_market_references(query):
    try:
        params = {"engine": "google_images", "q": f"{query} luxury car seat cover", "api_key": SERP_API_KEY, "num": 40}
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        filtered, used_sources = [], set()
        for i in results:
            src_name = i.get("source", "").strip()
            link = i.get("link", "").lower()
            if src_name in used_sources: continue
            if any(td in link for td in TRUSTED_DOMAINS):
                filtered.append({"img": i["original"], "link": i.get("link"), "src": src_name})
                used_sources.add(src_name)
            if len(filtered) >= 6: break
        if len(filtered) < 6:
            for i in results:
                src_name = i.get("source", "").strip()
                if src_name not in used_sources and "link" in i:
                    filtered.append({"img": i["original"], "link": i.get("link"), "src": src_name})
                    used_sources.add(src_name)
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
    
    custom_instruction = st.text_area("✍️ Engineering Instructions", placeholder="Add blue contrast stitching or specific perforation details...")

# --------------------------------------
# 🚀 SINGLE-THREAD EXECUTION
# --------------------------------------
if st.button("🚀 EXECUTE ENGINEERING SUITE"):
    final_prompt = (
        f"Professional automotive interior photography, {car} custom seat covers, "
        f"{pattern} pattern, premium {material}, {colors} theme, "
        f"{custom_instruction}, {lighting} lighting, 8k ultra-realistic, material macro detail."
    )
    
    with st.status("Processing Engineering Request...") as status:
        main_img = None
        if app_mode == "Pictator Refiner (Edit)":
            if uploaded_file:
                st.write("🔄 Refining uploaded design...")
                input_img = Image.open(uploaded_file)
                main_img = run_image_engine(final_prompt, input_img)
            else:
                st.error("⚠️ Please upload an image to use the Refiner mode.")
                st.stop()
        else:
            st.write("🎨 Generating base design...")
            main_img = run_image_engine(final_prompt)
            
        st.write("🌐 Verifying Unique Market Links...")
        market_refs = fetch_market_references(f"{car} {material} seat cover")
        
        st.write("📊 Finalizing RCA Analysis...")
        analysis = call_openrouter(f"Briefly analyze durability and 2026 trends for {material} with {pattern} stitching.")
        status.update(label="✅ Task Complete", state="complete")

    # --- DISPLAY RESULTS ---
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader(f"🖼️ {app_mode} Output")
        if main_img:
            st.image(main_img, use_container_width=True)
            buf = io.BytesIO()
            main_img.save(buf, format="PNG")
            st.download_button("💾 Save Prototype", buf.getvalue(), f"pictator_{int(time.time())}.png", "image/png")
        else:
            st.error("❌ Output Failed. Check if the HF Model is currently loading.")

    with col_right:
        st.subheader("📈 Flashmind Analysis")
        st.info(analysis)

    st.divider()
    st.subheader("🌍 Verified Unique Market References")
    if market_refs:
        m_cols = st.columns(3)
        for idx, ref in enumerate(market_refs):
            with m_cols[idx % 3]:
                st.image(ref["img"], use_container_width=True)
                st.link_button(f"🔗 View on {ref['src']}", ref["link"])
    else:
        st.warning("No unique market references found.")

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
    <b>Pictator Pro 2026</b> | Dual-Mode Engineering Engine | Zero Data Retention Protocol | © 2026 Harmony Engineering
</div>
""", unsafe_allow_html=True)
