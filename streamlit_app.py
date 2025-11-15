import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw

# -------------------------------------
# 🔐 HuggingFace API Token (Loaded Securely)
# -------------------------------------
HF_TOKEN = st.secrets["HF_TOKEN"]

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# -------------------------------------
# 📌 Function — Call FLUX API
# -------------------------------------
def generate_flux(prompt, width, height, guidance, steps):
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "guidance_scale": guidance,
            "num_inference_steps": steps
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        st.error("❌ API Error: " + response.text)
        return None

    data = response.json()

    # Standard HF Router format
    if "generated_image" in data:
        img_str = data["generated_image"]

    # Sometimes proxy returns list + blob
    elif isinstance(data, list) and "blob" in data[0]:
        img_str = data[0]["blob"]

    else:
        st.error("❌ Unexpected API format received")
        return None

    img_bytes = base64.b64decode(img_str)
    return Image.open(BytesIO(img_bytes))

# -------------------------------------
# ➕ Add Dimensions to Drawing
# -------------------------------------
def add_dimensions(img):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Horizontal dimension line
    draw.line((50, h - 60, w - 50, h - 60), fill="black", width=2)
    draw.line((50, h - 80, 50, h - 40), fill="black", width=2)
    draw.line((w - 50, h - 80, w - 50, h - 40), fill="black", width=2)

    # Dimension text
    text = f"{w} mm"
    draw.text((w // 2 - 40, h - 100), text, fill="black")

    return img

# -------------------------------------
# 🎨 Streamlit UI
# -------------------------------------
st.title("🎛 CNC Technical Drawing Generator (FLUX + HF Router API)")

prompt = st.text_area(
    "Enter Technical Prompt",
    "technical blueprint lineart of disc brake, top view, CNC style, thin lines, engineering drawing"
)

col1, col2, col3, col4 = st.columns(4)
width = col1.number_input("Width", 256, 1536, 768)
height = col2.number_input("Height", 256, 1536, 768)
guidance = col3.slider("Guidance Scale", 1.0, 8.0, 3.5)
steps = col4.slider("Inference Steps", 10, 80, 40)

add_dim = st.checkbox("Add CNC Dimensions", True)

if st.button("Generate Drawing"):
    with st.spinner("Generating CNC technical drawing..."):
        image = generate_flux(prompt, width, height, guidance, steps)

    if image:
        if add_dim:
            image = add_dimensions(image)

        st.image(image, caption="Generated CNC Blueprint", use_column_width=True)
        image.save("cnc_blueprint.png")
        st.success("Saved as cnc_blueprint.png")
