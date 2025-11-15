import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw

# ---------------------------------------------------
# 🔐 HuggingFace Token (from Streamlit App Secrets)
# ---------------------------------------------------
HF_TOKEN = st.secrets.get("HF_TOKEN")
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Accept": "application/json"
}

# ---------------------------------------------------
# ⚙️ Safe FLUX generation (handles ALL output formats)
# ---------------------------------------------------
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

    content_type = response.headers.get("content-type", "")

    # -------------------------------------------------
    # 🔹 CASE 1 — FLUX returns pure PNG binary
    # -------------------------------------------------
    if "image" in content_type:
        try:
            return Image.open(BytesIO(response.content))
        except:
            st.error("Failed to read PNG binary image.")
            return None

    # -------------------------------------------------
    # 🔹 CASE 2 — Try to decode JSON
    # -------------------------------------------------
    try:
        data = response.json()
    except Exception:
        st.error("HF API returned non-JSON text:\n\n" + response.text)
        return None

    # -------------------------------------------------
    # 🔹 CASE 3 — { "images": ["base64..."] }
    # -------------------------------------------------
    if isinstance(data, dict) and "images" in data:
        try:
            img_bytes = base64.b64decode(data["images"][0])
            return Image.open(BytesIO(img_bytes))
        except:
            pass

    # -------------------------------------------------
    # 🔹 CASE 4 — { "image": "base64..." }
    # -------------------------------------------------
    if "image" in data:
        try:
            img_bytes = base64.b64decode(data["image"])
            return Image.open(BytesIO(img_bytes))
        except:
            pass

    # -------------------------------------------------
    # 🔹 CASE 5 — { "generated_image": "base64..." }
    # -------------------------------------------------
    if "generated_image" in data:
        try:
            img_bytes = base64.b64decode(data["generated_image"])
            return Image.open(BytesIO(img_bytes))
        except:
            pass

    # -------------------------------------------------
    # 🔹 CASE 6 — { "output": "base64..." }
    # -------------------------------------------------
    if "output" in data:
        try:
            img_bytes = base64.b64decode(data["output"])
            return Image.open(BytesIO(img_bytes))
        except:
            pass

    # -------------------------------------------------
    # 🔹 CASE 7 — Router returns list output
    # -------------------------------------------------
    if isinstance(data, list):

        # { "blob": "base64..." }
        if "blob" in data[0]:
            try:
                img_bytes = base64.b64decode(data[0]["blob"])
                return Image.open(BytesIO(img_bytes))
            except:
                pass

        # { "generated_image": "base64..." }
        if "generated_image" in data[0]:
            try:
                img_bytes = base64.b64decode(data[0]["generated_image"])
                return Image.open(BytesIO(img_bytes))
            except:
                pass

    # -------------------------------------------------
    # 🔹 Unknown format
    # -------------------------------------------------
    st.error("❌ FLUX returned an unsupported format:\n\n" + str(data))
    return None


# ---------------------------------------------------
# ➕ Add CNC Dimensions
# ---------------------------------------------------
def add_dimensions(img):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # bottom dimension line
    draw.line((50, h - 60, w - 50, h - 60), fill="black", width=2)
    draw.line((50, h - 80, 50, h - 40), fill="black", width=2)
    draw.line((w - 50, h - 80, w - 50, h - 40), fill="black", width=2)

    # text (overall width)
    text = f"{w} mm"
    draw.text((w // 2 - 40, h - 100), text, fill="black")

    return img


# ---------------------------------------------------
# 🎛 Streamlit UI
# ---------------------------------------------------
st.title("🎛 CNC Technical Drawing Generator (FLUX via HF Router)")

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

