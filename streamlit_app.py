import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw

# ---------------------------------------------------
# 🔐 HuggingFace Token from Streamlit Secrets
# ---------------------------------------------------
HF_TOKEN = st.secrets.get("HF_TOKEN")

MODELS = {
    "2D Line Drawing (Best for CNC)": "stabilityai/sdxl-turbo",
    "3D Mechanical Render": "stabilityai/stable-diffusion-3-medium"
}

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

# ---------------------------------------------------
# Safe API Handler (works with PNG bytes + JSON)
# ---------------------------------------------------
def generate_image(model, prompt, width, height, steps, guidance):
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

    response = requests.post(url, headers=headers, json=payload)

    content_type = response.headers.get("content-type", "")

    # ---- Case 1 → Direct PNG image ----
    if "image" in content_type:
        return Image.open(BytesIO(response.content))

    # ---- Case 2 → JSON output ----
    try:
        data = response.json()
    except Exception:
        st.error("API returned non-JSON text:\n\n" + response.text)
        return None

    # ---- Case 3 → Standard HF router: { images: ["base64"] } ----
    if isinstance(data, dict) and "images" in data:
        try:
            img_b64 = data["images"][0]
            img_bytes = base64.b64decode(img_b64)
            return Image.open(BytesIO(img_bytes))
        except:
            st.error("Could not decode base64 image.")
            return None

    # ---- Unsupported format ----
    st.error("Unsupported API response:\n" + str(data))
    return None


# ---------------------------------------------------
# ➕ CNC Dimension Overlay (only for 2D)
# ---------------------------------------------------
def add_dimensions(img):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # basic dimension lines
    draw.line((50, h-50, w-50, h-50), fill="black", width=3)
    draw.line((50, h-70, 50, h-30), fill="black", width=3)
    draw.line((w-50, h-70, w-50, h-30), fill="black", width=3)

    # dimension text
    text = f"{w} mm"
    draw.text((w//2 - 40, h-100), text, fill="black")

    return img


# ---------------------------------------------------
# 🎛 Streamlit UI
# ---------------------------------------------------
st.title("🛠 CNC Blueprint & 3D Model Generator (HF Router API)")

model_choice = st.selectbox("Select Model Type", list(MODELS.keys()))
model_id = MODELS[model_choice]

prompt = st.text_area(
    "Enter Prompt",
    "technical CNC blueprint lineart of a disc brake, top view, thin black lines"
)

col1, col2 = st.columns(2)
width = col1.number_input("Width", 256, 1536, 768)
height = col2.number_input("Height", 256, 1536, 768)

steps = st.slider("Inference Steps", 5, 60, 20)
guidance = st.slider("Guidance Scale", 1.0, 8.0, 3.0)

add_dim = st.checkbox("Add CNC Dimensions (for 2D Blueprints Only)", True)

if st.button("Generate Drawing"):
    with st.spinner("Generating image..."):
        img = generate_image(model_id, prompt, width, height, steps, guidance)

    if img:
        # add dimensions only for 2D model
        if add_dim and "2D" in model_choice:
            img = add_dimensions(img)

        st.image(img, caption="Generated Output", use_column_width=True)

        img.save("output.png")
        st.success("Saved as output.png")
