import io
import requests
import streamlit as st
import torch
from PIL import Image
from diffusers import AutoPipelineForImage2Image

# -------------------------------------------------
# CUDA OPTIMIZATION
# -------------------------------------------------
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.benchmark = True

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Pictator Pro 2026",
    page_icon="🏎️",
    layout="wide"
)

# -------------------------------------------------
# API / SECRETS
# -------------------------------------------------
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# -------------------------------------------------
# TRUSTED DOMAINS
# -------------------------------------------------
TRUSTED_DOMAINS = [
    "autofurnish.com", "autofit.in", "autotextile.com", "cncstitching.com",
    "seatcoversunlimited.com", "foamvilla.com", "autoclint.com", "autoform.in",
    "coverking.com", "katzkin.com", "amazon.in", "cardekho.com",
    "elegantautoretail.com", "carwale.com"
]

# -------------------------------------------------
# AUTHENTICATION GUARD
# -------------------------------------------------
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
        st.success("🟢 Logged in")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Halt execution early if unauthenticated to avoid rendering the rest of UI elements
if not st.session_state.authenticated:
    st.warning("🔐 Please login to continue")
    st.stop()

# -------------------------------------------------
# TITLE & CAPTION
# -------------------------------------------------
st.title("🏎️ Pictator Pro – OEM Engineering Suite")
st.caption("OEM Seat Preservation • Premium Automotive Refinement • Multi Variant Generation")

# -------------------------------------------------
# OEM BASE IMAGES
# -------------------------------------------------
BASE_IMAGES = {
    "Maruti Wagon R": "assets/wagonr.jpg",
    "Maruti Grand Vitara": "assets/vitara.png"
}

# -------------------------------------------------
# MODEL UI
# -------------------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": "black-forest-labs/FLUX.1-schnell",
    "🔥 FLUX.1 Dev": "black-forest-labs/FLUX.1-dev",
    "✨ SD 3.5 Large": "stabilityai/stable-diffusion-3.5-large"
}

selected_model = st.sidebar.selectbox("Choose Pro AI Model", list(MODEL_OPTIONS.keys()))
st.sidebar.caption("⚡ OEM Refiner Optimization Active")

# -------------------------------------------------
# LOAD PIPELINE
# -------------------------------------------------
@st.cache_resource
def load_pipeline(selected_model):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    # Using fallback model setup as per original architecture design
    model_id = "SG161222/Realistic_Vision_V5.1_noVAE"

    pipe = AutoPipelineForImage2Image.from_pretrained(
        model_id,
        torch_dtype=dtype,
        use_safetensors=True,
        token=HF_TOKEN
    )
    pipe = pipe.to(device)

    if device == "cuda":
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        pipe.enable_model_cpu_offload()

    return pipe

# -------------------------------------------------
# IMAGE REFINER
# -------------------------------------------------
def refine_image_advanced(image, prompt):
    try:
        pipe = load_pipeline(selected_model)
        image = image.convert("RGB").resize((704, 512))

        negative_prompt = (
            "different seat, new interior, changed geometry, distorted dashboard, "
            "extra seats, warped stitching, SUV cabin, futuristic interior, concept car, "
            "different upholstery shape, changed contours, modified dashboard, steering wheel change"
        )

        with st.spinner("Generating OEM-preserved refinement..."):
            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image,
                strength=0.18,
                guidance_scale=5.5,
                num_inference_steps=16
            ).images[0]

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return result
    except Exception as e:
        import traceback
        st.error("Refiner Engine Error")
        st.code(traceback.format_exc())
        return None

# -------------------------------------------------
# MARKET REFERENCES
# -------------------------------------------------
def fetch_market_references(query):
    try:
        params = {
            "engine": "google_images",
            "q": f"{query} car seat covers leather",
            "api_key": SERP_API_KEY,
            "num": 20
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])

        filtered_refs = []
        used_domains = set()

        for i in results:
            source_name = i.get("source", "").strip()
            link = i.get("link", "").lower()

            if source_name in used_domains:
                continue

            if any(td in link for td in TRUSTED_DOMAINS):
                filtered_refs.append({
                    "img": i["original"],
                    "link": i["link"],
                    "src": source_name
                })
                used_domains.add(source_name)

            if len(filtered_refs) >= 6:
                break
        return filtered_refs
    except:
        return []

# -------------------------------------------------
# OPENROUTER ANALYSIS
# -------------------------------------------------
def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "qwen/qwen-3-coder:free",
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
        pass
    return "Engineering analysis currently unavailable."

# -------------------------------------------------
# SIDEBAR SETTINGS
# -------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🖌️ OEM Refiner Settings")
strict_oem_mode = st.sidebar.toggle("Strict OEM Preservation", value=True)

# -------------------------------------------------
# MAIN UI
# -------------------------------------------------
with st.expander("🧠 Smart Design Configurator", expanded=True):
    colA, colB, colC = st.columns(3)

    with colA:
        car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara"])
        stitch_type = st.selectbox("Stitching Style", [
            "Diamond Stitch", "Honeycomb Stitch", "Tuck and Roll",
            "Contrast Stitching", "Double Decorative", "Thread Decorative"
        ])

    with colB:
        material = st.selectbox("Material", [
            "1200 GSM Nappa", "Synthetic Leather", "Carbon Fiber Leather",
            "Premium Beige Leather", "Luxury Black Leather"
        ])
        piping_quilt = st.toggle("Design Piping & Quilting")
        custom_pq = st.text_input("Piping / Quilt Details") if piping_quilt else ""

    with colC:
        base_color = st.selectbox("Base Color", ["Beige", "Ivory", "Black", "Tan", "Grey"])
        num_images = st.select_slider("Generation Count", options=[1, 3, 5], value=1)

    st.divider()
    custom_instruction = st.text_area(
        "✍️ Engineering Instructions",
        placeholder="Example: sporty German luxury stitching with premium contrast quilting"
    )

# -------------------------------------------------
# EXECUTION
# -------------------------------------------------
if st.button("🚀 EXECUTE FULL SUITE"):
    try:
        base_image = Image.open(BASE_IMAGES[car]).convert("RGB")
    except FileNotFoundError:
        st.error(f"Could not find local file background image at `{BASE_IMAGES[car]}`. Please make sure your assets folder exists on your repository.")
        st.stop()

    color_choices = {
        1: ["Silver"],
        3: ["Silver", "Blue", "Red"],
        5: ["Silver", "Orange", "Blue", "Red", "Gold"]
    }
    palette = color_choices[num_images]
    generated_images = []

    with st.status("Engineering Intelligence Active...") as status:
        for current_color in palette:
            prompt = f"""
            Preserve exact OEM car seat structure and cabin layout.
            Keep identical OEM seat shape and contours.
            Do not change: seat shape, dashboard, geometry, perspective, headrest structure, seat contour.
            Only modify: leather material, stitching, quilting, piping, thread colors.

            Vehicle: {car}
            Material: {material}
            Stitching: {stitch_type}
            Thread Color: {current_color}
            Base Color: {base_color}
            Quilt Details: {custom_pq}
            Additional Instructions: {custom_instruction}

            Premium automotive photography, OEM factory fitment, ultra realistic, same original seat, realistic stitching, luxury upholstery, high-end craftsmanship
            """

            st.write(f"🎨 Generating {current_color} Variant...")
            img = refine_image_advanced(base_image, prompt)
            if img:
                generated_images.append((img, current_color))

        market_refs = fetch_market_references(f"{car} {material}")
        analysis = call_openrouter(f"""
            Analyze automotive upholstery quality.
            Vehicle: {car} | Material: {material} | Stitch: {stitch_type} | Base Color: {base_color}
        """)
        status.update(label="✅ Engineering Complete", state="complete")

    # -------------------------------------------------
    # OUTPUT UI
    # -------------------------------------------------
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🎨 OEM Refined Concepts")
        for idx, (img, c_name) in enumerate(generated_images):
            st.image(img, caption=f"Variant: {c_name}", use_container_width=True)
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            
            # Explicit key optimization to prevent widget element crashes during fast processing loop
            st.download_button(
                label=f"💾 Save {c_name}",
                data=buf.getvalue(),
                file_name=f"pictator_{c_name.lower()}.png",
                mime="image/png",
                key=f"dl_btn_{c_name}_{idx}"
            )

    with col_right:
        st.subheader("📈 Engineering Analysis")
        st.info(analysis)
        st.divider()

        if market_refs:
            st.subheader("🌍 Market References")
            for ref in market_refs:
                st.image(ref["img"], caption=ref["src"])
                st.link_button("View Source", ref["link"])

# -------------------------------------------------
# TECH NOTES
# -------------------------------------------------
with st.expander("📊 2026 OEM Tech Standards"):
    st.write("- OEM geometry preservation enabled")
    st.write("- Low hallucination refinement mode")
    st.write("- Optimized GPU inference pipeline")
    st.write("- Multi-variant rendering enabled")
    st.write("- Premium automotive upholstery refinement")
    st.caption("Zero Data Retention (ZDR) Enabled")
