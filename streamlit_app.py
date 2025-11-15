import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json

# -------------------------------
#  Hugging Face Token
# -------------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# -------------------------------
#  Supported Models (Only those proven working with HF Router)
# -------------------------------
MODELS = {
    "FLUX.1-dev (Lineart / Mechanical)": "black-forest-labs/FLUX.1-dev",
    "Stable Diffusion XL (2D CNC Blueprints)": "stabilityai/stable-diffusion-xl-base-1.0",
    "Stable Diffusion 3 Medium (3D Render)": "TensorStack/RealisticVision_v6-onnx"
}

# -------------------------------
# Safe HF Router Call
# -------------------------------
def safe_router_generate(model, prompt, width, height, steps, guidance):
    url = f"https://router.huggingface.co/hf-inference/models/{model}"

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": steps,
            "guidance_scale": guidance
        }
    }

    resp = requests.post(url, headers=headers, json=payload)

    # -------------------------------
    # 1. Handle No Body Returned
    # -------------------------------
    if not resp.content or resp.text.strip() == "":
        st.error("❌ Router returned EMPTY response.")
        return None

    # -------------------------------
    # 2. Try JSON First
    # -------------------------------
    try:
        data = resp.json()
        if "images" in data:
            img_data = base64.b64decode(data["images"][0])
            return Image.open(BytesIO(img_data))
    except:
        pass  # Continue to next checks

    # -------------------------------
    # 3. Check If Raw Image (PNG/JPEG)
    # -------------------------------
    if "image" in resp.headers.get("content-type", ""):
        return Image.open(BytesIO(resp.content))

    # -------------------------------
    # 4. Show Raw Response For Debugging
    # -------------------------------
    st.error("⚠ RAW HF ROUTER RESPONSE (NOT JSON):")
    st.code(resp.text)

    return None


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🛠 CNC Blueprint Generator (HF Router Stable Edition)")

prompt = st.text_area("Enter prompt",
    "high-precision technical blueprint, CAD lineart, orthographic projection,
mechanical disc brake assembly, thin blueprint lines, no shading, no textures,
engineering drawing syle, black lines on black background")

col1, col2 = st.columns(2)
width = col1.number_input("Width", 128, 1536, 768)
height = col2.number_input("Height", 128, 1536, 768)

steps = st.slider("Inference Steps", 5, 80, 25)
guidance = st.slider("Guidance Scale", 1.0, 20.0, 3.5)

model_choice = st.selectbox("Choose Model", list(MODELS.keys()))
model = MODELS[model_choice]

if st.button("Generate Blueprint"):
    with st.spinner("Generating..."):
        img = safe_router_generate(model, prompt, width, height, steps, guidance)

    if img:
        st.image(img, caption="Generated Output", use_column_width=True)
        img.save("output.png")
        st.success("Saved as output.png")
        st.download_button("Download PNG", open("output.png", "rb"), "output.png")
