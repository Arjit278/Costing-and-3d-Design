import streamlit as st
import requests
import base64
import json

# ------------------------------
# Hugging Face Token
# ------------------------------
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("🛠 CNC Blueprint Generator (Stable Edition)")

prompt = st.text_input("Enter prompt", 
                       "technical CNC blueprint lineart of disc brake, top view, thin black lines")

width = st.number_input("Width", 256, 2048, 768)
height = st.number_input("Height", 256, 2048, 768)
steps = st.slider("Inference Steps", 5, 50, 20)
guidance = st.slider("Guidance Scale", 1.0, 20.0, 5.0)

model = st.selectbox(
    "Choose Model",
    [
        "black-forest-labs/FLUX.1-schnell",
        "black-forest-labs/FLUX.1-dev",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "stabilityai/stable-diffusion-3-medium",
        "stabilityai/stable-diffusion-2-1"
    ]
)

if st.button("Generate Blueprint"):
    with st.spinner("Generating CNC drawing..."):

        # correct HF inference URL
        api_url = f"https://api-inference.huggingface.co/models/{model}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": steps,
                "guidance_scale": guidance,
            }
        }

        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if resp.status_code != 200:
                st.error(f"API Error: {resp.status_code}\n{resp.text}")
            else:
                data = resp.json()
                image_base64 = data[0]["generated_image"]
                image_bytes = base64.b64decode(image_base64)
                st.image(image_bytes, caption="Generated CNC Blueprint")

        except Exception as e:
            st.error(f"Error: {str(e)}")
