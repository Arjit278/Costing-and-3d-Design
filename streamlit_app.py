import streamlit as st
import pandas as pd
import time
import requests
import base64

# --- Hugging Face API Configuration ---
# WARNING: Exposing tokens in public code is a security risk.
# For production use, manage this token securely in Hugging Face Space secrets.
HF_TOKEN = "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"

def generate_image(prompt, width, height, steps, guidance, model_id):
    """Calls the Hugging Face router API to generate an image from a prompt."""
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

    # Handle both JSON responses (base64 encoded) and raw image bytes
    try:
        data = response.json()
        if "error" in data:
            st.error(f"API Error: {data['error']}")
            return None
        # base64 encoded
        img_base64 = data["generated_image"]
        return base64.b64decode(img_base64)
    except:
        # Try raw bytes if JSON parsing fails
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Raw API error: {response.text}")
            return None


# --- CNC Processing Functions (Placeholders) ---

def process_cad_file(uploaded_file):
    """
    Simulates processing a CAD file to generate G-code commands.
    In a real app, this would use a library (e.g., a custom parser or pygcode)
    to read the CAD data and convert it into G-code instructions.
    """
    st.write("Processing CAD file...")
    time.sleep(2) # Simulate processing time

    # Simulate G-code generation
    g_code_output = f"; G-code generated from {uploaded_file.name}\n"
    g_code_output += "G21 ; Set units to millimeters\n"
    g_code_output += "G90 ; Use absolute positioning\n"
    g_code_output += "M3 S1000 ; Spindle on, speed 1000 RPM\n"
    g_code_output += "G0 X0 Y0 Z10 ; Move to safe height\n"
    g_code_output += "G1 X10 Y10 Z0 F500 ; Move to start point, feed rate 500\n"
    g_code_output += "G1 X20 Y10 F500\n"
    g_code_output += "G1 X20 Y20 F500\n"
    g_code_output += "G1 X10 Y20 F500\n"
    g_code_output += "G1 X10 Y10 F500\n"
    g_code_output += "G0 Z10 ; Return to safe height\n"
    g_code_output += "M5 ; Spindle off\n"
    g_code_output += "M30 ; Program end\n"
    return g_code_output


# ==================================
# --- Streamlit UI Integration ---
# ==================================

st.title("Integrated CNC Design and Workflow Application")

# Use tabs to organize the two distinct features
tab1, tab2 = st.tabs(["💡 AI Design Generator", "🔄 CAD File to G-Code Workflow"])

with tab1:
    st.header("🛠 AI CNC Blueprint Generator")
    st.write("Generate 2D or 3D technical drawings from text prompts using Hugging Face models.")

    prompt = st.text_area("Enter prompt", 
                          "technical CNC blueprint lineart of disc brake, top view, thin black lines, engineering drawing",
                          key="design_prompt")

    # Layout parameters side-by-side
    col1, col2 = st.columns(2)
    with col1:
        width = st.number_input("Width", 512, key="width_input")
        height = st.number_input("Height", 512, key="height_input")
        steps = st.slider("Inference Steps", 5, 60, 30, key="steps_slider")
    with col2:
        guidance = st.slider("Guidance Scale", 1.0, 8.0, 3.5, key="guidance_slider")
        model_choice = st.selectbox(
            "Choose Model",
            [
                "black-forest-labs/FLUX.1-dev",
                "stabilityai/stable-diffusion-2-1",
                "timbrooks/instruct-pix2pix"
            ],
            key="model_select"
        )

    if st.button("Generate Drawing", key="generate_button"):
        with st.spinner("Generating CNC Drawing... this may take a moment."):
            img = generate_image(prompt, width, height, steps, guidance, model_choice)
            if img:
                st.image(img, caption="AI Generated CNC Design Output")
                # Optional: Add download button for the generated image
                st.download_button(
                    label="Download Image",
                    data=img,
                    file_name="generated_design.png",
                    mime="image/png"
                )

with tab2:
    st.header("🔄 G-Code Converter")
    st.write("Upload an existing CAD file (e.g., DXF, STL) to process and generate machine-ready G-code.")

    uploaded_file = st.file_uploader("Choose a CAD file", type=["dxf", "stl", "step", "iges"], key="cad_uploader")

    if uploaded_file is not None:
        st.subheader("File Details")
        st.write(f"File Name: {uploaded_file.name}")
        st.write(f"File Type: {uploaded_file.type}")
        st.write(f"File Size: {uploaded_file.size} bytes")

        if st.button("Generate G-code from CAD", key="process_cad_button"):
            with st.spinner('Generating G-code...'):
                g_code = process_cad_file(uploaded_file)
                st.success("G-code generated successfully!")

            st.subheader("Generated G-code Preview")
            st.code(g_code, language='gcode')

            st.download_button(
                label="Download G-code file",
                data=g_code,
                file_name="generated_output.nc",
                mime="text/plain"
            )
    else:
        st.info("Please upload a file to begin this workflow.")

