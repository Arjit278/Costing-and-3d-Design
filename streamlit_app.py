# ======================================================================
# CNC 2D + 3D TECHNICAL GENERATOR (HuggingFace Router - Fully Working)
# ======================================================================

import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64
import os

st.set_page_config(page_title="CNC 2D + 3D Generator (HF Router)", layout="wide")

# --------------------------------------------------
# SECRETS
# --------------------------------------------------
HF_TOKEN = st.secrets.get("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    st.error("HUGGINGFACE_TOKEN missing in Streamlit Secrets.")
    st.stop()

HEADERS_JSON = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}
HEADERS_RAW = {"Authorization": f"Bearer {HF_TOKEN}"}

# HF Router endpoints
TEXT_TO_IMAGE_URL = "https://router.huggingface.co/hf-inference/text-to-image"
THREE_URL = "https://router.huggingface.co/hf-inference/three"
MODEL_URL_BASE = "https://router.huggingface.co/hf-inference/models"

# --------------------------------------------------
# MODELS (ONLY SUPPORTED MODELS — NO “NOT FOUND”)
# --------------------------------------------------
MODELS_2D = {
    "SD15 Blueprint — Precision CAD style": "Onodofthenorth/SD15-Blueprint",
    "ControlNet Lineart — Sharp edges": "lllyasviel/sd-controlnet-lineart",
    "Stable Diffusion XL Base — Clean technical art": "stabilityai/stable-diffusion-xl-base-1.0",
    "Kandinsky 2.2 — Diagram style": "kandinsky-community/kandinsky-2-2-decoder"
}

MODELS_3D = {
    "TripoSR (image → 3D fast)": "stabilityai/TripoSR",
    "Zero123-XL (multi-view → 3D)": "ali-vilab/zero123-xl",
    "Shap-E (text → 3D)": "openai/shap-e"
}

DEPTH_MODEL = "LiheYoung/depth-anything-large-hf"


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def post_json(url, payload):
    return requests.post(url, headers=HEADERS_JSON, json=payload, timeout=120)


def post_file_to_model(model_repo, files_payload, params=None):
    url = f"{MODEL_URL_BASE}/{model_repo}"
    return requests.post(url, headers=HEADERS_RAW, files=files_payload, data=params or {}, timeout=120)


def decode_image_response(resp):
    try:
        return Image.open(BytesIO(resp.content))
    except:
        return None


# --------------------------------------------------
# 2D Image Generator
# --------------------------------------------------
def generate_2d(prompt, model_repo, steps=30, guidance_scale=3.5, width=768, height=768):
    payload = {
        "model": model_repo,
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": steps,
            "guidance_scale": guidance_scale,
            "height": height,
            "width": width
        }
    }

    r = post_json(TEXT_TO_IMAGE_URL, payload)

    if r.status_code != 200:
        return None, r.text

    # Try image bytes
    img = decode_image_response(r)
    if img:
        return img, None

    # Try base64 JSON
    try:
        j = r.json()
        if "image_base64" in j:
            b = base64.b64decode(j["image_base64"])
            return Image.open(BytesIO(b)), None
    except:
        pass

    return None, "Unknown router response."


# --------------------------------------------------
# Depth (Heightmap)
# --------------------------------------------------
def generate_depth_from_image(pil_img):
    buf = BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)

    files = {"data": ("image.png", buf, "image/png")}
    r = post_file_to_model(DEPTH_MODEL, files)

    if r.status_code != 200:
        return None, r.text

    img = decode_image_response(r)
    if img:
        return img, None

    # Try JSON
    try:
        j = r.json()
        if "depth" in j:
            d = base64.b64decode(j["depth"])
            return Image.open(BytesIO(d)), None
    except:
        pass

    return None, "Unknown depth model response."


# --------------------------------------------------
# 3D (Text → 3D)
# --------------------------------------------------
def generate_3d_text(prompt, model_repo):
    payload = {"model": model_repo, "inputs": prompt}
    r = post_json(THREE_URL, payload)

    if r.status_code != 200:
        return None, r.text

    ct = r.headers.get("content-type", "")

    # If router returns binary 3D data
    if "octet-stream" in ct or "model" in ct:
        return r.content, None

    # Base64 JSON fallback
    try:
        j = r.json()
        if "file" in j:
            return base64.b64decode(j["file"]), None
        if "data" in j:
            return base64.b64decode(j["data"]), None
    except:
        pass

    return None, "Unknown router 3D response."


# ======================================================================
# STREAMLIT UI
# ======================================================================

st.title("⚙️ CNC 2D + 3D Technical Designer (HuggingFace Router)")

tab2d, tab3d, tabdepth = st.tabs(["2D CNC BLUEPRINTS", "3D MODELS", "DEPTH MAP"])


# --------------------------------------------------
# 2D BLUEPRINTS
# --------------------------------------------------
with tab2d:
    st.header("2D Technical CNC Drawing Generator")

    model_choice = st.selectbox("Choose a technical drawing model", list(MODELS_2D.keys()))

    prompt_2d = st.text_area(
        "Prompt",
        "technical precision blueprint of a disc brake rotor, CAD style, thin black lines, top-view, mechanical drawing"
    )

    steps = st.slider("Inference steps", 10, 50, 30)
    scale = st.slider("Guidance scale", 1.0, 8.0, 3.5, step=0.1)

    colw, colh = st.columns(2)
    with colw:
        width = st.selectbox("Width", [512, 640, 768, 1024], index=2)
    with colh:
        height = st.selectbox("Height", [512, 640, 768, 1024], index=2)

    if st.button("Generate 2D Blueprint"):
        with st.spinner("Generating CNC technical drawing..."):
            img, err = generate_2d(prompt_2d, MODELS_2D[model_choice], steps, scale, width, height)
            if err:
                st.error(err)
            else:
                st.image(img, caption="CNC Blueprint Output", use_column_width=True)
                buf = BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                st.download_button("Download PNG", buf, "cnc_blueprint.png", "image/png")


# --------------------------------------------------
# 3D MODELS
# --------------------------------------------------
with tab3d:
    st.header("3D Engineering Model Generator")

    mode = st.radio("Generation Mode", ["Text → 3D (Shap-E / Zero123)", "Image → 3D (TripoSR)"])

    if "Text" in mode:
        model_3d = st.selectbox("Select 3D Model", list(MODELS_3D.keys()))
        prompt_3d = st.text_area("3D Object Prompt", "precision mechanical rotor 3D model")

        if st.button("Generate 3D from Text"):
            with st.spinner("Generating 3D model..."):
                data, err = generate_3d_text(prompt_3d, MODELS_3D[model_3d])
                if err:
                    st.error(err)
                else:
                    st.success("3D model ready")
                    st.download_button("Download 3D Model (.obj)", data, "cnc_3d.obj", "model/obj")

    else:
        upload = st.file_uploader("Upload an image for 3D conversion (TripoSR)", ["jpg", "jpeg", "png"])
        if upload and st.button("Generate 3D from Image"):
            with st.spinner("Processing through TripoSR..."):
                files = {"data": ("image.png", upload.getvalue(), "image/png")}
                r = post_file_to_model(MODELS_3D["TripoSR"], files)

                if r.status_code != 200:
                    st.error(r.text)
                else:
                    st.success("TripoSR returned a 3D model")
                    st.download_button("Download 3D OBJ", r.content, "tripo_3d.obj", "model/obj")


# --------------------------------------------------
# DEPTH / HEIGHTMAP
# --------------------------------------------------
with tabdepth:
    st.header("Depth & Heightmap (Useful for CNC routing)")

    file = st.file_uploader("Upload image", ["jpg", "jpeg", "png"])

    if file and st.button("Generate Heightmap"):
        img = Image.open(file).convert("RGB")
        with st.spinner("Estimating depth..."):
            depth, err = generate_depth_from_image(img)
            if err:
                st.error(err)
            else:
                st.image(depth, caption="Depth Map", use_column_width=True)
                buf = BytesIO()
                depth.save(buf, format="PNG")
                buf.seek(0)
                st.download_button("Download Depth PNG", buf, "depth_map.png", "image/png")
