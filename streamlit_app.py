import streamlit as st
import pandas as pd
import time
import requests
import base64
# Ensure you have the 'huggingface_hub' and 'Pillow' libraries installed
from huggingface_hub import InferenceClient 

# --- Hugging Face API Configuration (Reads securely from secrets file) ---
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except KeyError:
    st.error("HF_TOKEN secret not found. Please add it to the App Settings > Secrets.")
    st.stop() # Stops the script if the token is missing

# Initialize the client (model is set later during the request)
client = InferenceClient(token=HF_TOKEN)

def generate_image_hf_hub(prompt, width, height, steps, guidance, model_id):
    """Uses the huggingface_hub client to generate an image."""
    try:
        # The client handles the request and authentication
        image_bytes = client.text_to_image(
            model=model_id,
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance,
        )
        # Convert PIL image to bytes for Streamlit
        import io
        img_byte_arr = io.BytesIO()
        image_bytes.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    except Exception as e:
        st.error(f"API Error using huggingface_hub: {e}")
        # Check if the error suggests a bad token or specific model issue
        if "Authentication" in str(e) or "invalid" in str(e).lower():
            st.warning("The API token might be invalid or the model requires different permissions.")
        return None

# --- CNC Processing Functions (Placeholders) ---

def process_cad_file(uploaded_file):
    """
    Simulates processing a CAD file to generate G-code commands.
    """
    st.write("Processing CAD file...")
    time.sleep(2) 
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

tab1, tab2 = st.tabs(["💡 AI Design Generator", "🔄 CAD File to G-Code Workflow"])

with tab1:
    st.header("🛠 AI CNC Blueprint Generator")
    st.write("Generate 2D or 3D technical drawings from text prompts using Hugging Face models.")

    prompt = st.text_area("Enter prompt", 
                          "technical CNC blueprint lineart of disc brake, top view, thin black lines, engineering drawing",
                          key="design_prompt")

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
                "stabilityai/stable-diffusion-2-1",
                "timbrooks/instruct-pix2pix",
            ],
            key="model_select"
        )

    if st.button("Generate Drawing", key="generate_button"):
        with st.spinner("Generating CNC Drawing... this may take a moment."):
            img = generate_image_hf_hub(prompt, width, height, steps, guidance, model_choice)
            if img:
                st.image(img, caption="AI Generated CNC Design Output")
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
