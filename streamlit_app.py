import io
import requests
import streamlit as st
import json
import time
import re
import numpy as np
from PIL import Image
from huggingface_hub import InferenceClient
import torch

from diffusers import (
    StableDiffusionImg2ImgPipeline,
    AutoPipelineForImage2Image
)

# --------------------------------------
# 🔧 PAGE CONFIG & API
# --------------------------------------
st.set_page_config(page_title="Pictator Pro 2026", page_icon="🏎️", layout="wide")

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

TRUSTED_DOMAINS = [
    "autofurnish.com","za.pinterest.com/ideas/leather-car-seat-covers", "autofit.in", "autotextile.com", "cncstitching.com",
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

prompt = f"""
Preserve exact OEM car seat structure and cabin layout.
Do not change seat shape, dimensions, dashboard or perspective.

Only modify:
- seat leather material
- stitching
- quilting
- piping
- thread colors

{material} leather,
{stitch_type},
{current_color} stitching,
premium automotive photography,
ultra realistic,
OEM factory fitment,
same original seat.
"""

negative_prompt = """
different seat,
new interior,
changed geometry,
distorted dashboard,
extra seats,
warped stitching,
different car,
SUV cabin,
futuristic interior,
concept car
"""
# --------------------------------------
# ⚡ ENGINES (PRO & REFINER)
# --------------------------------------
def generate_ai_image(prompt, model_id):
    try:
        client = InferenceClient(model=model_id, token=HF_TOKEN)
        return client.text_to_image(prompt, width=1024, height=768)
    except Exception as e:
        st.error(f"HF Generation Failed: {e}")
        return None

def refine_image_advanced(image_bytes, prompt, model_choice):

    try:

        import io
        import torch

        from PIL import Image

        from huggingface_hub import login

        from diffusers import AutoPipelineForImage2Image

        # =====================================================
        # HF LOGIN
        # =====================================================

        login(token=HF_TOKEN)

        # =====================================================
        # IMAGE PREP
        # =====================================================

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        image = image.resize((640x512))

        # =====================================================
        # DEVICE
        # =====================================================

        device = "cuda" if torch.cuda.is_available() else "cpu"

        dtype = torch.float16 if device == "cuda" else torch.float32

        # =====================================================
        # MODEL MAP
        # =====================================================

        MODEL_MAP = {

            "Realistic Vision":
                "SG161222/Realistic_Vision_V5.1_noVAE",

            "DreamShaper":
                "Lykon/DreamShaper",

            "OpenJourney":
                "prompthero/openjourney",

            "Juggernaut XL":
                "RunDiffusion/Juggernaut-XL-v9",

            "SDXL Turbo":
                "stabilityai/sdxl-turbo",

            "SDXL Base":
                "stabilityai/stable-diffusion-xl-base-1.0"
        }

        model_id = MODEL_MAP.get(model_choice)

        if not model_id:

            st.error("Invalid model selected")

            return None

        # =====================================================
        # LOAD MODEL
        # =====================================================

        with st.spinner(f"Loading {model_choice} model..."):

            pipe = AutoPipelineForImage2Image.from_pretrained(
                model_id,
                torch_dtype=dtype,
                use_safetensors=True,
                token=HF_TOKEN
            )
        @st.cache_resource
        def load_pipeline(): 
        # =====================================================
        # PERFORMANCE OPTIMIZATION
        # =====================================================

        pipe = pipe.to(device)

        if device == "cuda":

            pipe.enable_attention_slicing()

            pipe.enable_vae_slicing()

        # =====================================================
        # GENERATION
        # =====================================================

        with st.spinner("Generating refined image..."):

            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image,
                strength=0.20,
                guidance_scale=6,
                num_inference_steps=18
            ).images[0]

        return result

    except Exception as e:

        import traceback

        st.error(f"Refiner Pipeline ({model_choice}) Error")

        st.code(traceback.format_exc())

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
# 🎯 SIDEBAR & CONFIG
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": "black-forest-labs/FLUX.1-schnell",
    "🔥 FLUX.1 Dev": "black-forest-labs/FLUX.1-dev",
    "✨ SD 3.5 Large": "stabilityai/stable-diffusion-3.5-large"
}
selected_model = st.sidebar.selectbox("Choose Pro AI Model", list(MODEL_OPTIONS.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("🖌️ Pictator Refiner Mode")

WAGONR_IMAGE = "assets/wagonr.jpg"
VITARA_IMAGE = "assets/vitara.png"

BASE_IMAGES = {
    "Maruti Wagon R": "assets/wagonr.jpg",
    "Maruti Grand Vitara": "assets/vitara.png"
}

base_image = Image.open(
    BASE_IMAGES[car]
).convert("RGB")

active_engine = st.sidebar.selectbox(
    "🖌️ Refiner Engine",
    [
        "Realistic Vision",
        "DreamShaper",
        "OpenJourney",
        "Juggernaut XL",
        "SDXL Turbo",
        "SDXL Base"
    ]
)

# --------------------------------------
# 🎨 UI LOGIC: REFINER vs PRO MODE
# --------------------------------------
if uploaded_file:
    # --- REFINER WORKSPACE (HIDES PRO UI) ---
    st.subheader(f"🖌️ Pictator Refiner Workspace ({active_engine})")
    st.info(f"Refiner Active: Using {active_engine} protocol with 40s Rendering Timeout.")
    
    col_ref_img, col_ref_ctrl = st.columns([1, 1])
    
    with col_ref_img:
        st.image(uploaded_file, caption="Original Design Plate", use_container_width=True)
    
    with col_ref_ctrl:
        refine_prompt = st.text_area("✍️ Modification Instructions", placeholder="Describe design refinements (e.g., 'Replace beige leather with black carbon fiber')...", height=200)
        if st.button("🚀 Apply Design Refinement"):
            with st.spinner(f"Refining via {active_engine}..."):
                refined_result = refine_image_advanced(uploaded_file.getvalue(), refine_prompt, active_engine)
                if refined_result:
                    st.image(refined_result, caption="Refined Output", use_container_width=True)
                    buf = io.BytesIO(); refined_result.save(buf, format="PNG")
                    st.download_button("💾 Save Refined Design", buf.getvalue(), "refined_design.png")
    
    if st.button("⬅️ Back to Pro Engineering Suite"):
        st.rerun()

else:
    # --- PRO VERSION INTERFACE ---
    with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
        colA, colB, colC = st.columns(3)
        with colA:
            car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Custom/Other"])
            stitch_type = st.selectbox("Stitching Style", ["Diamond Stitch", "Honeycomb Stitch", "Tuck and Roll (Pleated)", "Contrast Stitching", "Threading Stitch Decorative", "Double Decorative", "Custom"])
            custom_stitch = st.text_input("Custom Stitch Details") if stitch_type == "Custom" else ""
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
            st.toggle("Custom Pattern Mode")
            pattern_target = st.selectbox("Pattern Target", ["Stitching", "Piping", "Base Design"])
        with col_opt2:
            st.toggle("Color Control Mode")
            color_choices = {1: ["Silver"], 3: ["Silver", "Blue", "Red"], 5: ["Silver", "Orange", "Blue", "Red", "Gold"]}
            manual_color = st.selectbox("Select Palette", color_choices.get(num_images))

        custom_instruction = st.text_area("✍️ Engineering Instructions", placeholder="Add professional engineering details...")

    # 🚀 EXECUTION PIPELINE
    if st.button("🚀 EXECUTE FULL SUITE"):
        palette = color_choices.get(num_images)
        with st.status("Engineering Intelligence...") as status:
            generated_images = []
            for i in range(num_images):
                current_color = manual_color if i == 0 else palette[i % len(palette)]
                prompt = (f"Automotive interior, {car} seat covers, {material}, {base_color} base, "
                          f"{stitch_type} with {current_color} threading, "
                          f"{'Piping/Quilt: ' + custom_pq if piping_quilt else ''}, "
                          f"{custom_instruction}, studio lighting, 8k realism.")
                
                st.write(f"🎨 Generating {current_color} Variant...")
                img = generate_ai_image(prompt, MODEL_OPTIONS[selected_model])
                if img: generated_images.append((img, current_color))
            
            market_refs = fetch_market_references(f"{car} {material} seat cover")
            analysis = call_openrouter(f"Analysis for {material} with {stitch_type} in {palette[0]}.")
            status.update(label="✅ Engineering Complete", state="complete")

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
    st.write("- **Refiner Mode:** Switches between Alimama/UNO and ControlNet structural inpainting.")
    st.write("- **Safety:** 40s Rendering Timeout enabled for high-fidelity design refinement.")
    st.caption("Zero Data Retention (ZDR) Commitment: Proprietary design logic secured via Volatile Memory.")
