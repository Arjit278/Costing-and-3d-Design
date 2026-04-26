import io
import json
import requests
import streamlit as st
import zipfile
import time
from PIL import Image
from huggingface_hub import InferenceClient

# --------------------------------------
# 🔧 PAGE CONFIG & THEME
# --------------------------------------
st.set_page_config(page_title="Pictator Pro 2026", page_icon="🏎️", layout="wide")

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# 🔐 AUTH & STATE
# --------------------------------------
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "count" not in st.session_state: st.session_state.count = 0

# Sidebar login (unchanged as per your request)
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
        st.success("🟢 Logged in as Harmony")

if not st.session_state.authenticated:
    st.warning("🔐 Please login to continue")
    st.stop()

# --------------------------------------
# 🎨 MODEL CONFIG (HF 2026 STACK)
# --------------------------------------
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")

MODEL_OPTIONS = {
    "⚡ FLUX Schnell (Fastest)": "black-forest-labs/FLUX.1-schnell",
    "🔥 Krea Dev (High Detail)": "black-forest-labs/FLUX.1-dev",
    "⚡ SDXL Lightning": "ByteDance/SDXL-Lightning"
}
selected_model = st.sidebar.selectbox("Choose Generation Model", list(MODEL_OPTIONS.keys()))
ACTIVE_MODEL = MODEL_OPTIONS[selected_model]

# --------------------------------------
# 🛠️ IMAGE ENGINES
# --------------------------------------
def generate_ai_image(prompt):
    """Generates image using HF InferenceClient (More stable for 2026)"""
    try:
        client = InferenceClient(api_key=HF_TOKEN)
        # Fixed: Explicitly handle the PIL object return
        image = client.text_to_image(prompt, model=ACTIVE_MODEL)
        return image
    except Exception as e:
        st.sidebar.error(f"HF Generation Failed: {e}")
        return None

def fetch_market_images(query):
    """Fetches real market photos via SERP API"""
    try:
        params = {
            "engine": "google_images",
            "q": f"{query} 2026 luxury car seat cover leather",
            "api_key": SERP_API_KEY,
            "num": 8
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        return [img.get("original") for img in results if "original" in img]
    except:
        return []

# --------------------------------------
# 🎯 SMART BUILDER UI
# --------------------------------------
with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
    colA, colB, colC = st.columns(3)
    with colA:
        car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara"])
        pattern = st.selectbox("Stitching", ["Ultra-Quilt Diamond", "Hex-Cell", "Minimalist Flat"])
    with colB:
        material = st.selectbox("Material", ["1200 GSM Nappa", "Carbon Fiber Leather"])
        colors = st.text_input("Colorway", "Tan & Charcoal")
    with colC:
        lighting = st.selectbox("Lighting", ["Studio", "Showroom"])
        market = st.selectbox("Market", ["Luxury", "OEM Upgrade"])

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE FULL SUITE"):
    final_prompt = f"Professional automotive interior photography, {car} seat covers, {pattern} {material}, {colors} theme, ultra-detailed 8k, studio lighting"
    
    with st.status("Engineering Intelligence...") as status:
        # 1. Main Design
        st.write("🎨 Rendering Main Design Concept...")
        main_img = generate_ai_image(final_prompt)
        
        # 2. Market Sourcing
        st.write("🌐 Fetching Verified Market References...")
        market_photos = fetch_market_images(f"{car} {material} seat cover")
        
        status.update(label="✅ Analysis Complete", state="complete")

    # --- DISPLAY MAIN IMAGE ---
    st.subheader("🎨 Featured Design Concept")
    if main_img:
        st.image(main_img, use_container_width=True)
        # Download button for main image
        buf = io.BytesIO()
        main_img.save(buf, format="PNG")
        st.download_button("💾 Save Concept", buf.getvalue(), "design_2026.png", "image/png")
    else:
        st.error("❌ Main image failed. Check HF_TOKEN in Secrets.")

    # --- DISPLAY MARKET LINKS & PHOTOS (6-8 LINKS) ---
    st.subheader("🌍 Verified Market Links & Reference Designs")
    
    verified_sites = [
        {"name": "Autofurnish", "url": "https://www.autofurnish.com"},
        {"name": "Stanley", "url": "https://www.stanleyoutfitters.com"},
        {"name": "Elegant Auto", "url": "https://www.elegantauto.in"},
        {"name": "Autoform", "url": "https://www.autoform.in"},
        {"name": "Katzkin", "url": "https://www.katzkin.com"},
        {"name": "Coverking", "url": "https://www.coverking.com"},
        {"name": "CarID", "url": "https://www.carid.com"}
    ]

    # Grid Display for Market Photos + Links
    if market_photos:
        cols = st.columns(3)
        for idx, photo_url in enumerate(market_photos[:6]):
            with cols[idx % 3]:
                st.image(photo_url, caption=f"Ref: {verified_sites[idx]['name']}", use_container_width=True)
                st.link_button(f"Visit {verified_sites[idx]['name']}", verified_sites[idx]['url'])
    else:
        st.warning("⚠️ Market photos couldn't be loaded. Check SERP_API_KEY.")

# --------------------------------------
# 🎨 DIRECT RENDER
# --------------------------------------
if st.sidebar.button("🎨 QUICK RENDER"):
    with st.spinner("Generating..."):
        quick_img = generate_ai_image(f"Macro shot of {material} leather with {pattern} stitching, 8k")
        if quick_img:
            st.sidebar.image(quick_img)
            st.session_state.count += 1
