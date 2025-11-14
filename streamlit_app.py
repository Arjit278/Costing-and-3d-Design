import streamlit as st
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="CNC 2D + 3D AI Generator", layout="wide")

# --- Load secret token ---
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# --- HuggingFace Model URLs ---
MODELS_2D = {
    "Flux Dev (Best for Mechanical Images)": "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
    "Blueprint Style (CNC Drawings)": "https://api-inference.huggingface.co/models/Onodofthenorth/SD15-Blueprint",
    "Lineart (Technical Edges)": "https://api-inference.huggingface.co/models/lllyasviel/sd-controlnet-lineart"
}

MODELS_3D = {
    "TripoSR (Fast 3D Reconstruction)": "https://api-inference.huggingface.co/models/stabilityai/TripoSR",
    "Zero123-XL (Rotation Based 3D)": "https://api-inference.huggingface.co/models/ali-vilab/zero123-xl",
    "Shap-E (Lightweight 3D)": "https://api-inference.huggingface.co/models/openai/shap-e"
}

# --- Image Generation ---
def hf_image_api(prompt, model_url):
    payload = {"inputs": prompt}
    r = requests.post(model_url, headers=headers, json=payload)
    if r.status_code != 200:
        st.error(r.text)
        return None
    return Image.open(BytesIO(r.content))

# --- 3D Generation (returns files) ---
def hf_3d_api(prompt, model_url):
    payload = {"inputs": prompt}
    r = requests.post(model_url, headers=headers, json=payload)
    if r.status_code != 200:
        st.error(r.text)
        return None
    return r.content  # binary 3D file (OBJ/GLB)

# --- UI ---
st.title("⚙️ CNC 2D & 3D AI Generator (Fast | Accurate | Cloud Models)")
st.write("No local model required. All models run on HuggingFace GPUs.")

tab2d, tab3d = st.tabs(["📐 2D CNC Drawings", "🧱 3D CNC Models"])

# ===========================
# 2D CNC DRAWING TAB
# ===========================
with tab2d:
    st.subheader("2D Technical / CNC Drawing Generator")
    model_2d = st.selectbox("Select 2D Model", list(MODELS_2D.keys()))
    prompt_2d = st.text_area("Enter prompt", 
        "technical drawing lineart of a mechanical gearbox, blueprint style"
    )

    if st.button("Generate 2D Drawing"):
        with st.spinner("Generating 2D CNC drawing..."):
            img = hf_image_api(prompt_2d, MODELS_2D[model_2d])
            if img:
                st.image(img, use_column_width=True)
                img.save("cnc_2d.png")
                st.download_button(
                    "Download PNG", 
                    data=open("cnc_2d.png", "rb"), 
                    file_name="cnc_2d.png"
                )

# ===========================
# 3D CNC MODEL TAB
# ===========================
with tab3d:
    st.subheader("3D CNC Model Generator (OBJ/GLB)")
    model_3d = st.selectbox("Select 3D Model", list(MODELS_3D.keys()))
    prompt_3d = st.text_area("Enter 3D prompt", 
        "3D model of a precision-engineered mechanical shaft assembly"
    )

    if st.button("Generate 3D Model"):
        with st.spinner("Generating 3D file..."):
            file_data = hf_3d_api(prompt_3d, MODELS_3D[model_3d])
            if file_data:
                st.success("3D model generated!")
                st.download_button(
                    "Download 3D File",
                    data=file_data,
                    file_name="cnc_3d_model.obj"
                )
