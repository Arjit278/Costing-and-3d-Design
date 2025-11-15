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
st.title("🛠 CNC Blueprint Generator (HF Router Stable Edition)")

prompt = st.text_area("Enter prompt", 
                      "technical CNC blueprint lineart of disc brake, thin black lines, engineering drawing")

width = st.number_input("Width", 256, 2048, 768)
height = st.number_input("Height", 256, 2048, 768)
steps = st.slider("Inference Steps", 5, 60, 20)
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

        # ✔ Correct new HF Router URL
        api_url = f"https://router.huggingface.co/hf-inference/models/{model}"

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
            resp = requests.post(api_url, headers=headers, json=payload, timeout=40)

            if resp.status_code != 200:
                st.error(f"API Error {resp.status_code}: {resp.text}")
            else:
                data = resp.json()
                image_base64 = data[0].get("generated_image")

                if not image_base64:
                    st.error("No image returned. Model may not support the requested parameters.")
                else:
                    image_bytes = base64.b64decode(image_base64)
                    st.image(image_bytes, caption="Generated CNC Blueprint")

                    st.download_button(
                        "Download Image",
                        data=image_bytes,
                        file_name="blueprint.png",
                        mime="image/png"
                    )

        except Exception as e:
            st.error(f"Error: {str(e)}")
