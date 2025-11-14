import streamlit as st
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="CNC 2D + 3D AI Generator", layout="wide")

# ====== IMPORTANT ======
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

BASE_URL = "https://router.huggingface.co/hf-inference/v1/models"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ============================
# Model Names
# ============================

MODELS_2D = {
    "Flux Dev (Best for mechanical)": "black-forest-labs/FLUX.1-dev",
    "Blueprint Style": "Onodofthenorth/SD15-Blueprint",
    "Lineart ControlNet": "lllyasviel/sd-controlnet-lineart",
}

MODELS_3D = {
    "TripoSR (Fast 3D Reconstruction)": "stabilityai/TripoSR",
    "Zero123-XL": "ali-vilab/zero123-xl",
    "Shap-E": "openai/shap-e"
}

# =============================
# TEXT → IMAGE (2D)
# =============================
def generate_image(prompt, model):
    url = f"{BASE_URL}/{model}"

    payload = {
        "inputs": prompt
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error(response.text)
        return None

    return Image.open(BytesIO(response.content))


# =============================
# TEXT → 3D (OBJ / GLB)
# =============================
def generate_3d_file(prompt, model):
    url = f"{BASE_URL}/{model}"

    payload = {
        "inputs": prompt
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error(response.text)
        return None

    return response.content


# ==========================================================
# UI
# ==========================================================

st.title("⚙️ CNC 2D & 3D AI Generator (HF Router API Edition)")
st.write("Fully cloud-based. No model downloads. Fast & optimized.")

tab2d, tab3d = st.tabs(["📐 2D CNC Drawings", "🧱 3D CNC Models"])

# =============================
# 2D TAB
# =============================
with tab2d:
    st.subheader("Generate 2D Technical Drawings / CNC Blueprints")

    model_2d = st.selectbox("Select Model", list(MODELS_2D.keys()))
    prompt_2d = st.text_area(
        "Enter Prompt",
        "technical blueprint lineart of mechanical gear assembly, top-down view"
    )

    if st.button("Generate 2D Drawing"):
        with st.spinner("Rendering 2D CNC drawing…"):
            img = generate_image(prompt_2d, MODELS_2D[model_2d])

        if img:
            st.image(img, use_column_width=True)
            img.save("cnc_2d.png")

            st.download_button(
                "Download Image",
                data=open("cnc_2d.png", "rb"),
                file_name="cnc_2d.png",
                mime="image/png"
            )


# =============================
# 3D TAB
# =============================
with tab3d:
    st.subheader("Generate 3D CNC Models (OBJ / GLB)")

    model_3d = st.selectbox("Select 3D Model", list(MODELS_3D.keys()))
    prompt_3d = st.text_area(
        "Enter 3D Prompt",
        "3d model of a precision machined turbine rotor, mechanical part"
    )

    if st.button("Generate 3D Model"):
        with st.spinner("Building 3D mesh…"):
            file_data = generate_3d_file(prompt_3d, MODELS_3D[model_3d])

        if file_data:
            st.success("3D Model ready!")

            st.download_button(
                "Download 3D File",
                data=file_data,
                file_name="cnc_3d_model.obj",
                mime="model/obj"
            )
