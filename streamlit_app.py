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

    # Case 1 → Direct PNG bytes
    if "image" in content_type:
        return Image.open(BytesIO(response.content))

    # Case 2 → JSON
    try:
        data = response.json()
    except:
        st.error("API returned non-JSON error:\n\n" + response.text)
        return None

    # JSON → { images: ["base64..."] }
    if "images" in data:
        img_data = data["images"][0]
        return Image.open(BytesIO(base64.b64decode(img_data)))

    st.error("Unsupported API response:\n" + str(data))
    return None


# ---------------------------------------------------
# ➕ Add CNC Dimensions
# ---------------------------------------------------
def add_dimensions(img):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    draw.line((50, h-60, w-50, h-60), fill="black", width=2)
    draw.line((50, h-80, 50, h-40), fill="black", width=2)
    draw.line((w-50, h-80, w-50, h-40), fill="black", width=2)

    text = f"{w} mm"
    draw.text((w//2 - 40, h-110), text, fill="black")

    return img


# ---------------------------------------------------
# 🎛 Streamlit UI
# ---------------------------------------------------
st.title("🛠 CNC Blueprint & 3D Model Generator (HF Router)")

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

add_dim = st.checkbox("Add CNC Dimensions (Only for 2D mode)", True)

if st.button("Generate"):
    with st.spinner("Generating image..."):
        img = generate_image(model_id, prompt, width, height, steps, guidance)

    if img:
        if add_dim and "2D" in model_choice:
            img = add_dimensions(img)

        st.image(img, caption="Generated Output", use_column_width=True)

        img.save("output.png")
        st.success("Saved as output.png")
