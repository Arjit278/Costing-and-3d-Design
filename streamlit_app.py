import requests
import base64
import streamlit as st

HF_TOKEN = "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"

def generate_image(prompt, width, height, steps, guidance, model_id):
    url = "https://router.huggingface.co/hf-inference"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "X-Model": model_id,
        "Content-Type": "application/json"
    }

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

    # Some HF responses are raw image bytes (NOT JSON)
    try:
        data = response.json()

        if "error" in data:
            st.error(f"API Error: {data['error']}")
            return None

        # base64 encoded
        img_base64 = data["generated_image"]
        return base64.b64decode(img_base64)

    except:
        # Try raw bytes
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Raw API error: {response.text}")
            return None


# ==== UI ====

st.title("🛠 CNC Blueprint Generator (HF Router Stable Edition)")

prompt = st.text_area("Enter prompt", 
                      "technical CNC blueprint lineart of disc brake, top view, thin black lines, engineering drawing")

width = st.number_input("Width", 512)
height = st.number_input("Height", 512)

steps = st.slider("Inference Steps", 5, 60, 30)
guidance = st.slider("Guidance Scale", 1.0, 8.0, 3.5)

model_choice = st.selectbox(
    "Choose Model",
    [
        "black-forest-labs/FLUX.1-dev",   # best detail
        "stabilityai/stable-diffusion-2-1",
        "timbrooks/instruct-pix2pix"
    ]
)

if st.button("Generate"):
    with st.spinner("Generating CNC Drawing..."):
        img = generate_image(prompt, width, height, steps, guidance, model_choice)
        if img:
            st.image(img, caption="CNC Drawing Output")
