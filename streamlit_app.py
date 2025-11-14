# streamlit_app.py
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64
import os

st.set_page_config(page_title="CNC 2D + 3D Generator (HF Router)", layout="wide")

# ---------- Secrets ----------
HF_TOKEN = st.secrets.get("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    st.error("HUGGINGFACE_TOKEN not found. Add it to Streamlit Secrets or environment.")
    st.stop()

HEADERS_JSON = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}
HEADERS_RAW = {"Authorization": f"Bearer {HF_TOKEN}"}

# ---------- Endpoints ----------
TEXT_TO_IMAGE_URL = "https://router.huggingface.co/hf-inference/text-to-image"
THREE_URL = "https://router.huggingface.co/hf-inference/three"
MODEL_URL_BASE = "https://router.huggingface.co/hf-inference/models"  # for model-specific endpoints that accept files

# ---------- Recommended models ----------
MODELS_2D = {
    "Flux Dev (mechanical detail)": "black-forest-labs/FLUX.1-dev",
    "SD15-Blueprint (blueprint style)": "Onodofthenorth/SD15-Blueprint",
    "ControlNet-Lineart (clean lines)": "lllyasviel/sd-controlnet-lineart"
}

MODELS_3D = {
    "TripoSR (image->3D fast)": "stabilityai/TripoSR",
    "Zero123-XL (multi-view)": "ali-vilab/zero123-xl",
    "Shap-E (text->3D)": "openai/shap-e"
}

DEPTH_MODEL = "LiheYoung/depth-anything-large-hf"

# ---------- Helpers ----------
def post_json(url, payload):
    r = requests.post(url, headers=HEADERS_JSON, json=payload, timeout=120)
    return r

def post_file_model(model_repo, files_payload, params=None):
    """
    Upload files (image) to a model endpoint.
    Uses: https://router.huggingface.co/hf-inference/models/{model_repo}
    """
    url = f"{MODEL_URL_BASE}/{model_repo}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    r = requests.post(url, headers=headers, files=files_payload, data=params or {}, timeout=120)
    return r

def decode_image_response(resp):
    """Try to decode a response as an image (common case)."""
    try:
        return Image.open(BytesIO(resp.content))
    except Exception:
        return None

# ---------- Generation functions ----------
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
    img = decode_image_response(r)
    if img:
        return img, None
    # try JSON with base64
    try:
        j = r.json()
        if isinstance(j, dict) and "image_base64" in j:
            b = base64.b64decode(j["image_base64"])
            return Image.open(BytesIO(b)), None
    except Exception:
        pass
    return None, "Unknown response format"

def generate_depth_from_image(pil_img):
    # send image file to depth model
    buf = BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    files = {"data": ("image.png", buf, "image/png")}
    r = post_file_model(DEPTH_MODEL, files)
    if r.status_code != 200:
        return None, r.text
    # depth model often returns image bytes or JSON array; try image first
    img = decode_image_response(r)
    if img:
        return img, None
    try:
        j = r.json()
        # some models return {"depth": base64}
        if "depth" in j:
            depth_b64 = j["depth"]
            depth_bytes = base64.b64decode(depth_b64)
            return Image.open(BytesIO(depth_bytes)), None
    except Exception:
        pass
    return None, "Unknown depth response format"

def generate_3d_text(prompt, model_repo):
    payload = {
        "model": model_repo,
        "inputs": prompt
    }
    r = post_json(THREE_URL, payload)
    if r.status_code != 200:
        return None, r.text
    # router three endpoint should return binary 3D file (obj/glb) or JSON with base64
    # try interpret as binary file
    ct = r.headers.get("content-type", "")
    if "application/octet-stream" in ct or "model" in ct or ct == "application/octet-stream":
        return r.content, None
    # try JSON with "data" or "file" base64
    try:
        j = r.json()
        if "file" in j:
            return base64.b64decode(j["file"]), None
        if "data" in j:
            return base64.b64decode(j["data"]), None
    except Exception:
        pass
    return None, "Unknown 3D response format"

# ---------- Streamlit UI ----------
st.title("⚙️ CNC 2D + 3D Generator (HuggingFace Router)")

tab2d, tab3d, tabdepth = st.tabs(["2D CNC Drawings", "3D Model Generation", "Depth / Heightmap"])

# -------- 2D Tab --------
with tab2d:
    st.header("2D CNC / Blueprint generation")
    model_choice = st.selectbox("Choose a 2D model", list(MODELS_2D.keys()))
    prompt_2d = st.text_area("Prompt (example):", "technical blueprint lineart of a disc brake, top view, clean lines")
    steps = st.slider("Inference steps", 10, 50, 30)
    scale = st.slider("Guidance scale", 1.0, 8.0, 3.5, step=0.5)
    size_w, size_h = st.columns(2)
    with size_w:
        width = st.selectbox("Width", [512, 640, 768, 1024], index=2)
    with size_h:
        height = st.selectbox("Height", [512, 640, 768, 1024], index=2)

    if st.button("Generate 2D CNC Image"):
        with st.spinner("Generating 2D image on HuggingFace..."):
            img, err = generate_2d(prompt_2d, MODELS_2D[model_choice], steps, scale, width, height)
            if err:
                st.error(err)
            else:
                st.image(img, caption="Generated CNC image", use_column_width=True)
                buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
                st.download_button("Download PNG", data=buf, file_name="cnc_2d.png", mime="image/png")

# -------- 3D Tab --------
with tab3d:
    st.header("3D Model generation (text → 3D / image → 3D)")
    mode = st.radio("Mode", ["Text → 3D (Shap-E / Zero123)", "Image → 3D (TripoSR)"])
    if mode.startswith("Text"):
        model3 = st.selectbox("Choose 3D text model", list(MODELS_3D.keys()))
        prompt_3d = st.text_area("3D prompt (example):", "3D model of a precision disc brake rotor, manifolds and holes")
        if st.button("Generate 3D (Text)"):
            with st.spinner("Generating 3D file..."):
                bin_file, err = generate_3d_text(prompt_3d, MODELS_3D[model3])
                if err:
                    st.error(err)
                else:
                    st.success("3D model generated")
                    st.download_button("Download 3D file", data=bin_file, file_name="cnc_3d_model.obj", mime="model/obj")
    else:
        st.write("Upload an image (PNG/JPG) to reconstruct 3D via TripoSR")
        upload = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        if upload:
            if st.button("Generate 3D (Image)"):
                with st.spinner("Sending image to TripoSR..."):
                    files = {"data": ("image.png", upload.getvalue(), "image/png")}
                    r = post_file_model(MODELS_3D["TripoSR"], files)
                    if r.status_code != 200:
                        st.error(r.text)
                    else:
                        # assume returned binary 3D model
                        ct = r.headers.get("content-type", "")
                        data = r.content
                        st.success("TripoSR returned a file")
                        st.download_button("Download 3D (from TripoSR)", data=data, file_name="tripo_3d_model.obj", mime="model/obj")

# -------- Depth Tab --------
with tabdepth:
    st.header("Depth / Heightmap (Depth-Anything)")
    upload_img = st.file_uploader("Upload image for depth estimation", type=["png", "jpg", "jpeg"])
    if upload_img and st.button("Estimate Depth"):
        img = Image.open(upload_img).convert("RGB")
        with st.spinner("Estimating depth..."):
            depth_img, err = generate_depth_from_image(img)
            if err:
                st.error(err)
            else:
                st.image(depth_img, caption="Estimated depth", use_column_width=True)
                buf = BytesIO(); depth_img.save(buf, format="PNG"); buf.seek(0)
                st.download_button("Download depth PNG", data=buf, file_name="depth.png", mime="image/png")
