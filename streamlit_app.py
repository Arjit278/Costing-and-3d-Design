import io
import base64
import requests
import streamlit as st
from PIL import Image

# ------------------------------
# 🔐 SIMPLE LOGIN SYSTEM
# ------------------------------
st.set_page_config(page_title="Pictator Creator Cloud", layout="wide")

st.title("🔐 Login Required")

# Hardcoded user/pass for Streamlit Cloud
VALID_USERNAME = "admin"
VALID_PASSWORD = "1234"

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid Username or Password")
    st.stop()

# ------------------------------
# 🎨 After Login: Pictator Creator (Tab 4 Only)
# ------------------------------

st.title("🎨 Pictator Creator (HF Router Only)")

HF_TOKEN = st.sidebar.text_input("HuggingFace Token (HF_TOKEN)", type="password")

# ------------------------------
# HF Router Running Function (Image Generator)
# ------------------------------
HF_ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

def hf_router_generate_image(model_repo: str, prompt: str, hf_token: str,
                             width=1024, height=1024, steps=30, guidance=3.5):

    if not hf_token:
        return {"type": "error", "data": "[HF_TOKEN missing]"}

    url = f"{HF_ROUTER_BASE}/{model_repo}"
    headers = {"Authorization": f"Bearer {hf_token}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": steps,
            "guidance_scale": guidance
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
    except Exception as e:
        return {"type": "error", "data": f"[HF Router request failed: {e}]"}

    # Direct Image
    if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
        try:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            return {"type": "image", "data": img}
        except Exception as e:
            return {"type": "error", "data": f"[HF decode failed: {e}]"}

    # JSON fallback
    try:
        data = resp.json()
    except:
        return {"type": "error", "data": resp.text[:400]}

    try:
        if isinstance(data, dict) and "generated_image" in data:
            img_bytes = base64.b64decode(data["generated_image"])
            return {"type": "image", "data": Image.open(io.BytesIO(img_bytes)).convert("RGB")}

        if isinstance(data, dict) and "images" in data:
            img_bytes = base64.b64decode(data["images"][0])
            return {"type": "image", "data": Image.open(io.BytesIO(img_bytes)).convert("RGB")}
    except Exception as e:
        return {"type": "error", "data": f"[HF parse error: {e}]"}

    return {"type": "error", "data": f"Unsupported response: {data}"}


# ------------------------------
# UI – Pictator Creator Only
# ------------------------------

st.subheader("Create Engineering Drawing using HF Router Models")

MODELS = {
    "Sketchers (Lineart / Mechanical)": "black-forest-labs/FLUX.1-dev",
    "CAD Drawing XL (2D CNC Blueprints)": "stabilityai/stable-diffusion-xl-base-1.0",
    "RealisticVision (3D)": "stabilityai/stable-diffusion-3-medium-diffusers"
}

model_choice = st.selectbox("Model", list(MODELS.keys()))

prompt = st.text_area(
    "Prompt",
    "technical CNC blueprint, mechanical disc brake, top view, thin black engineering lineart"
)

col1, col2 = st.columns(2)
with col1:
    width = st.number_input("Width", 256, 1536, 768)
with col2:
    height = st.number_input("Height", 256, 1536, 768)

steps = st.slider("Inference Steps", 5, 80, 30)
guidance = st.slider("Guidance Scale", 1.0, 12.0, 3.5)

if st.button("Generate"):
    with st.spinner("Generating image from HuggingFace Router..."):
        repo = MODELS[model_choice]
        out = hf_router_generate_image(
            repo, prompt, HF_TOKEN,
            width=width, height=height,
            steps=steps, guidance=guidance
        )

    if out["type"] == "image":
        img = out["data"]
        st.image(img, caption="Generated Drawing", use_column_width=True)

        buf = io.BytesIO()
        img.save(buf, "PNG")
        st.download_button("Download PNG", buf.getvalue(), "pictator.png")
    else:
        st.error(out["data"])
