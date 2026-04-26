import io
import requests
import streamlit as st
from PIL import Image
from huggingface_hub import InferenceClient

# --------------------------------------
# 🔧 PAGE CONFIG
# --------------------------------------
st.set_page_config(page_title="Pictator Pro 2026", page_icon="🏎️", layout="wide")

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# 🔐 SECRETS & AUTH
# --------------------------------------
# Ensure these are set in your .streamlit/secrets.toml
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")

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
    st.warning("🔐 Please login to continue")
    st.stop()

# --------------------------------------
# 🎨 MODEL CONFIG (2026 Optimized)
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": "black-forest-labs/FLUX.1-schnell",
    "🔥 FLUX.1 Dev": "black-forest-labs/FLUX.1-dev",
    "✨ Stable Diffusion 3.5": "stabilityai/stable-diffusion-3.5-large"
}
selected_model = st.sidebar.selectbox("Choose Generation Model", list(MODEL_OPTIONS.keys()))
ACTIVE_MODEL = MODEL_OPTIONS[selected_model]

# --------------------------------------
# 🛠️ IMAGE ENGINES
# --------------------------------------
def generate_ai_image(prompt):
    if not HF_TOKEN:
        st.error("Missing HF_TOKEN in Secrets!")
        return None
    try:
        # Initialize client with token
        client = InferenceClient(model=ACTIVE_MODEL, token=HF_TOKEN)
        image = client.text_to_image(
            prompt,
            width=1024,
            height=768,
            num_inference_steps=4 if "schnell" in ACTIVE_MODEL.lower() else 28
        )
        return image
    except Exception as e:
        st.sidebar.error(f"HF Error: {e}")
        return None

def fetch_market_images(query):
    try:
        params = {
            "engine": "google_images",
            "q": f"{query} luxury interior leather 2026",
            "api_key": SERP_API_KEY,
            "num": 6
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        return [img.get("original") for img in r.json().get("images_results", [])]
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
        lighting = st.selectbox("Lighting", ["Studio Photography", "Cinematic Showroom"])
        market = st.selectbox("Market", ["Luxury", "OEM Upgrade"])

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE FULL SUITE"):
    # Refined prompt for "Proper Designing"
    final_prompt = (
        f"High-end automotive interior design, close-up of {car} custom seat covers, "
        f"{pattern} pattern, premium {material}, {colors} color scheme, "
        f"meticulous stitching detail, {lighting}, 8k resolution, highly realistic, "
        f"commercial automotive photography."
    )
    
    with st.status("Engineering Intelligence...") as status:
        st.write("🎨 Rendering Main Design Concept...")
        main_img = generate_ai_image(final_prompt)
        
        st.write("🌐 Fetching Verified Market References...")
        market_photos = fetch_market_images(f"{car} {material} seat cover")
        
        status.update(label="✅ Analysis Complete", state="complete")

    st.subheader("🎨 Featured Design Concept")
    if main_img:
        st.image(main_img, use_container_width=True)
        buf = io.BytesIO()
        main_img.save(buf, format="PNG")
        st.download_button("💾 Save Concept", buf.getvalue(), "design_2026.png", "image/png")
    else:
        st.error("Main image failed. Please verify your HF_TOKEN permissions.")

    st.subheader("🌍 Verified Market Links & Reference Designs")
    if market_photos:
        cols = st.columns(3)
        for idx, photo_url in enumerate(market_photos[:6]):
            with cols[idx % 3]:
                st.image(photo_url, use_container_width=True)
                st.caption(f"Market Reference {idx+1}")
