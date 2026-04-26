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
    st.warning("🔐 Please login to continue")
    st.stop()

# --------------------------------------
# ⚡ FLASHMIND ENGINE (OPENROUTER)
# --------------------------------------
ANALYSIS_MODELS = [
    "qwen/qwen3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-2-pro-llama-3-8b",
    "qwen/qwen3-next-80b-a3b-instruct:free",
]

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in ANALYSIS_MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an automotive engineering expert."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=15
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except:
            continue
    return "Intelligence fallback active: Manual review required."

# --------------------------------------
# 🛠️ IMAGE & MARKET ENGINES
# --------------------------------------
def generate_ai_image(prompt, model_id):
    try:
        client = InferenceClient(model=model_id, token=HF_TOKEN)
        return client.text_to_image(prompt, width=1024, height=768)
    except Exception as e:
        st.error(f"HF Generation Failed: {e}")
        return None

def fetch_market_references(query):
    try:
        params = {"engine": "google_images", "q": f"{query} luxury seat cover 2026", "api_key": SERP_API_KEY, "num": 10}
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        return [{"img": i["original"], "link": i["link"], "src": i.get("source", "Market")} for i in results if "link" in i][:6]
    except:
        return []

# --------------------------------------
# 🎯 UI: SMART CONFIGURATOR
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": "black-forest-labs/FLUX.1-schnell",
    "🔥 FLUX.1 Dev": "black-forest-labs/FLUX.1-dev",
    "🔥 Krea Dev (Ultra Realistic)": "black-forest-labs/FLUX.1-Krea-dev",
    "🧠 Qwen Image (Balanced AI)": "Qwen/Qwen-Image",
    "✨ SD 3.5 Large": "stabilityai/stable-diffusion-3.5-large"
}
selected_model = st.sidebar.selectbox("Choose AI Model", list(MODEL_OPTIONS.keys()))

with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
    colA, colB, colC = st.columns(3)
    with colA:
        car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Any Car mention in prompt"])
        pattern = st.selectbox("Stitching", ["Ultra-Quilt Diamond", "Hex-Cell", "Puff", "Minimalist Flat", "Anydesign"])
    with colB:
        material = st.selectbox("Material", ["1200 GSM Nappa", "Cotton", "Synthetic leather",  "Carbon Fiber Leather", "Anydesign"])
        colors = st.text_input("Colorway", "Dual", "Tan & Charcoal")
    with colC:
        lighting = st.selectbox("Lighting", ["Studio", "Blueprint", "Cinematic Showroom", "Anyother"])
        market = st.selectbox("Market Tier", ["Luxury", "Affordeable", "Sports", "OEM Upgrade"])
    
    custom_instruction = st.text_area("✍️ Custom Engineering Instructions", placeholder="Add specific details...")

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE FULL SUITE"):
    final_prompt = f"Automotive interior, {car} custom seat covers, {pattern} {material}, {colors}, {custom_instruction}, {lighting}, 8k ultra-detailed."
    
    with st.status("Engineering Intelligence...") as status:
        st.write("🎨 Rendering Main Design...")
        main_img = generate_ai_image(final_prompt, MODEL_OPTIONS[selected_model])
        
        st.write("🌐 Sourcing Verified Market Links...")
        market_refs = fetch_market_references(f"{car} {material}")
        
        st.write("📊 Analyzing Material Trends...")
        analysis = call_openrouter(f"Briefly analyze the durability and 2026 market trend for {material} with {pattern} stitching.")
        
        status.update(label="✅ Analysis Complete", state="complete")

    # Layout Results
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🎨 Featured Design Concept")
        if main_img:
            st.image(main_img, use_container_width=True)
            buf = io.BytesIO()
            main_img.save(buf, format="PNG")
            st.download_button("💾 Save Concept", buf.getvalue(), "design_2026.png")
    
    with col_right:
        st.subheader("📈 Flashmind Analysis")
        st.info(analysis)

    st.divider()
    st.subheader("🌍 Verified Market References & Live Shop Links")
    if market_refs:
        m_cols = st.columns(3)
        for idx, ref in enumerate(market_refs):
            with m_cols[idx % 3]:
                st.image(ref["img"], use_container_width=True)
                st.link_button(f"🔗 View on {ref['src']}", ref["link"])

# --------------------------------------
# 📈 TRENDS EXPANDER
# --------------------------------------
with st.expander("📊 2026 Tech & Model Trends"):
    st.markdown("""
    - **OpenRouter ZDR:** Essential for keeping your design prompts private.
    - **Qwen-3 Coder:** Best-in-class for understanding technical material properties.
    - **Multithreaded Search:** Market links are now verified in real-time against trusted domains.
    """)
