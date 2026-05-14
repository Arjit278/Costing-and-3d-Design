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

# --- CEO TRUSTED DOMAIN LIST (2026 Master List) ---
TRUSTED_DOMAINS = [
    "autofurnish.com", "autofit.in", "autotextile.com", "cncstitching.com",
    "seatcoversunlimited.com", "foamvilla.com", "sa.made-in-china.com",
    "autoclint.com", "autoform.in", "coverking.com", "katzkin.com",
    "amazon.in", "cardekho.com", "elegantautoretail.com", "carwale.com"
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
    st.warning("🔐 Please login to continue")
    st.stop()

# --------------------------------------
# ⚡ ENGINES
# --------------------------------------
def generate_ai_image(prompt, model_id):
    try:
        client = InferenceClient(model=model_id, token=HF_TOKEN)
        return client.text_to_image(prompt, width=1024, height=768)
    except Exception as e:
        st.error(f"HF Generation Failed: {e}")
        return None

def refine_image(image_bytes, prompt):
    """REFINER: Fast, Prompt-Based Clean Editing"""
    try:
        # Utilizing SDXL Refiner for efficient, professional-grade I2I refinement
        client = InferenceClient(model="stabilityai/stable-diffusion-xl-refiner-1.0", token=HF_TOKEN)
        return client.image_to_image(image_bytes, prompt=prompt, strength=0.45)
    except Exception as e:
        st.error(f"Refiner Error: {e}")
        return None

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers,
            json={"model": "qwen/qwen-3-coder:free", "messages": [{"role": "system", "content": "You are an automotive engineering expert."}, {"role": "user", "content": prompt}]}, timeout=15)
        if r.status_code == 200: return r.json()["choices"][0]["message"]["content"].strip()
    except: pass
    return "Intelligence fallback active: Manual review required."

def fetch_market_references(query):
    try:
        params = {"engine": "google_images", "q": f"{query} car seat covers leather", "api_key": SERP_API_KEY, "num": 40}
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        filtered_refs = []
        used_domains = set()
        for i in results:
            source_name = i.get("source", "").strip()
            link = i.get("link", "").lower()
            if source_name in used_domains: continue
            if any(td in link for td in TRUSTED_DOMAINS):
                filtered_refs.append({"img": i["original"], "link": i["link"], "src": source_name})
                used_domains.add(source_name)
            if len(filtered_refs) >= 6: break
        return filtered_refs
    except: return []

# --------------------------------------
# 🎯 SIDEBAR CONFIG
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": "black-forest-labs/FLUX.1-schnell",
    "🔥 FLUX.1 Dev": "black-forest-labs/FLUX.1-dev",
    "✨ SD 3.5 Large": "stabilityai/stable-diffusion-3.5-large"
}
selected_model = st.sidebar.selectbox("Choose AI Model", list(MODEL_OPTIONS.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("🖌️ Pictator Refiner")
uploaded_file = st.sidebar.file_uploader("Upload Image to Start Refiner", type=["png", "jpg", "jpeg"])

# --------------------------------------
# 🎨 UI LOGIC: REFINER vs PRO MODE
# --------------------------------------
if uploaded_file:
    # --- REFINER WORKSPACE (HIDES PRO CONFIGURATOR) ---
    st.subheader("🖌️ Pictator Refiner Workspace")
    st.info("Focused Editing Mode: Pro tools hidden for design refinement.")
    
    col_ref_img, col_ref_ctrl = st.columns([1, 1])
    
    with col_ref_img:
        st.image(uploaded_file, caption="Original Design", use_container_width=True)
    
    with col_ref_ctrl:
        refine_prompt = st.text_area("✍️ Refiner Prompt", placeholder="Describe changes (e.g., 'Change stitching to blue')...", height=200)
        if st.button("✨ Apply Refined Changes"):
            with st.spinner("Refining Design..."):
                refined_result = refine_image(uploaded_file.getvalue(), refine_prompt)
                if refined_result:
                    st.image(refined_result, caption="Refined Output", use_container_width=True)
                    buf = io.BytesIO()
                    refined_result.save(buf, format="PNG")
                    st.download_button("💾 Save Refined Design", buf.getvalue(), "refined_pictator.png")
    
    if st.button("⬅️ Exit Refiner / Back to Pro"):
        st.rerun()

else:
    # --- PRO VERSION INTERFACE ---
    with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
        colA, colB, colC = st.columns(3)
        with colA:
            car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Custom/Other"])
            stitch_type = st.selectbox("Stitching Style", ["Diamond Stitch", "Honeycomb Stitch", "Tuck and Roll (Pleated)", "Contrast Stitching", "Threading Stitch Decorative", "Double Decorative", "Custom"])
            custom_stitch = st.text_input("Custom Stitch Prompt") if stitch_type == "Custom" else ""
        with colB:
            material = st.selectbox("Material", ["1200 GSM Nappa", "Cotton", "Synthetic Leather", "Carbon Fiber Leather"])
            piping_quilt = st.toggle("Design Piping & Quilting")
            custom_pq = st.text_input("Custom Piping/Quilt Prompt") if piping_quilt else ""
        with colC:
            base_color_toggle = st.toggle("Base Colors")
            base_color = st.selectbox("Color", ["Beige", "Ivory", "Black"]) if base_color_toggle else "Tan & Charcoal"
            num_images = st.select_slider("Generation Count", options=[1, 3, 5])

        st.divider()
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            custom_pattern_toggle = st.toggle("Custom Pattern")
            pattern_target = st.selectbox("Target Element", ["Stitching", "Piping", "Base Design"]) if custom_pattern_toggle else "Overall"
        with col_opt2:
            custom_color_toggle = st.toggle("Color Control")
            color_choices = {1: ["Silver"], 3: ["Silver", "Blue", "Red"], 5: ["Silver", "Orange", "Blue", "Red", "Gold"]}
            manual_color = st.selectbox("Accent Color", color_choices.get(num_images)) if custom_color_toggle else None

        custom_instruction = st.text_area("✍️ Custom Engineering Instructions", placeholder="Add professional engineering details...")

    # 🚀 EXECUTION PIPELINE
    if st.button("🚀 EXECUTE FULL SUITE"):
        palette = color_choices.get(num_images)
        with st.status("Engineering Design...") as status:
            generated_images = []
            for i in range(num_images):
                current_color = manual_color if (custom_color_toggle and i == 0) else palette[i % len(palette)]
                prompt = (f"Automotive interior, {car} seat covers, {material}, {base_color} base, "
                          f"{stitch_type} with {current_color} threading, "
                          f"{'Piping/Quilt: ' + custom_pq if piping_quilt else ''}, "
                          f"{custom_instruction}, studio lighting, 8k realism.")
                
                st.write(f"🎨 Generating {current_color} Variant...")
                img = generate_ai_image(prompt, MODEL_OPTIONS[selected_model])
                if img: generated_images.append((img, current_color))
            
            market_refs = fetch_market_references(f"{car} {material} seat cover")
            analysis = call_openrouter(f"Analysis for {material} with {stitch_type} in {palette[0]}.")
            status.update(label="✅ Complete", state="complete")

        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.subheader("🎨 AI-Generated Concepts")
            for img, c_name in generated_images:
                st.image(img, caption=f"Variant: {c_name}", use_container_width=True)
                buf = io.BytesIO(); img.save(buf, format="PNG")
                st.download_button(f"💾 Save {c_name}", buf.getvalue(), f"pictator_{c_name}.png")
        with col_right:
            st.subheader("📈 Analysis")
            st.info(analysis)
            st.divider()
            if market_refs:
                st.subheader("🌍 Market Refs")
                for ref in market_refs: 
                    st.image(ref["img"], caption=ref["src"])
                    st.link_button("View Shop", ref["link"])

with st.expander("📊 2026 Tech Standards"):
    st.write("- **Refiner Mode:** Full-screen prompt-based editing on uploaded design.")
    st.write("- **Dynamic Threading:** 1, 3, 5 image counts auto-cycle professional palettes.")
    st.caption("Zero Data Retention (ZDR) Commitment: Proprietary design logic secured via Volatile Memory.")
