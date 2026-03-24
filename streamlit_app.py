import io
import json
import requests
import streamlit as st
import re
import threading
from PIL import Image

# --------------------------------------
# 🔧 PAGE CONFIG
# --------------------------------------
st.set_page_config(page_title="Pictator Pro", page_icon="🏎️", layout="wide")

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# SESSION
# --------------------------------------
if "count" not in st.session_state:
    st.session_state.count = 0

st.sidebar.title("🔐 Control Panel")
st.sidebar.metric("🖼️ Images Generated", st.session_state.count)
st.sidebar.markdown("---")

# --------------------------------------
# RESULT CONTAINER
# --------------------------------------
class AnalysisResults:
    def __init__(self):
        self.rca_intel = None
        self.specs_raw = None
        self.market_photos = []
        self.ai_concept = None
        self.rca_status = "OK"

# --------------------------------------
# API CONFIG (UPDATED)
# --------------------------------------
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

MODELS = ["meta-llama/llama-3.2-3b-instruct:free"]

# --------------------------------------
# OPENROUTER ENGINE
# --------------------------------------
def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    last_error = None

    for model in MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=35
            )

            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if content:
                    return content.strip(), "OK"
            else:
                last_error = f"HTTP {r.status_code}"

        except Exception as e:
            last_error = str(e)

    return None, last_error or "Timeout"

# --------------------------------------
# IMAGE ENGINE
# --------------------------------------
def hf_gen_image(prompt):
    try:
        url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except:
        return None

# --------------------------------------
# THREADS
# --------------------------------------
def thread_rca(res, prompt):
    try:
        output, status = call_openrouter(
            f"""
            Generate current automotive trends for:

            {prompt}

            Rules:
            - Strictly match domain
            - Use real technologies/materials
            - 5 bullet points
            - No generic statements
            """
        )
        res.rca_intel = output
        res.rca_status = status
    except Exception as e:
        res.rca_intel = None
        res.rca_status = str(e)


def thread_meta(res, prompt):
    try:
        result = call_openrouter(
            f"""
            Generate 3 real automotive vendors based on:

            {prompt}

            Requirements:
            - Real companies (Bosch, Valeo, Hella, Lear, Faurecia, etc.)
            - Correct domain materials
            - Include vehicle examples
            - Include official website links

            Return JSON:
            [
              {{
                "Brand": "",
                "Vehicle": "",
                "Country": "",
                "Type": "",
                "Material": "",
                "Strength": "",
                "Website": ""
              }}
            ]
            """
        )
        res.specs_raw = result[0] if result else None
    except:
        res.specs_raw = None


def thread_assets(res, prompt):
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={"engine": "google_images", "q": prompt, "api_key": SERP_API_KEY},
            timeout=10
        )
        res.market_photos = r.json().get("images_results", [])[:3]
    except:
        res.market_photos = []

    res.ai_concept = hf_gen_image(f"{prompt}, automotive engineering diagram")

# --------------------------------------
# UI INPUT
# --------------------------------------
prompt = st.text_area("Enter Topic")

col1, col2 = st.columns(2)

# --------------------------------------
# EXECUTION
# --------------------------------------
if col1.button("🚀 EXECUTE"):
    if not prompt:
        st.warning("Enter prompt")
    else:
        res = AnalysisResults()

        with st.status("Running engines...", expanded=True):
            t1 = threading.Thread(target=thread_rca, args=(res, prompt))
            t2 = threading.Thread(target=thread_meta, args=(res, prompt))
            t3 = threading.Thread(target=thread_assets, args=(res, prompt))

            t1.start()
            t2.start()
            t3.start()

            t1.join(timeout=45)
            t2.join(timeout=25)
            t3.join(timeout=35)

        # --------------------------------------
        # CURRENT TRENDS (FULLY DYNAMIC)
        # --------------------------------------
        if not res.rca_intel:
            st.warning(f"⚠️ Primary Engine Failed: {res.rca_status}")

            trend_output, _ = call_openrouter(f"Generate trends for: {prompt}")
            res.rca_intel = trend_output or f"No trends available for: {prompt}"

        st.subheader("📊 Current Trends")
        st.write(res.rca_intel)

        # --------------------------------------
        # IMAGE + COUNTER
        # --------------------------------------
        if res.ai_concept:
            st.image(res.ai_concept)
            st.session_state.count += 1

        # --------------------------------------
        # SPECS
        # --------------------------------------
        specs = []
        try:
            match = re.search(r"\[.*\]", str(res.specs_raw), re.DOTALL)
            if match:
                specs = json.loads(match.group())
        except:
            specs = []

        # FINAL DYNAMIC FALLBACK
        if not specs:
            fallback_prompt = f"Generate automotive vendors for: {prompt} with JSON"
            ai_specs, _ = call_openrouter(fallback_prompt)

            if ai_specs:
                match = re.search(r"\[.*\]", ai_specs, re.DOTALL)
                if match:
                    specs = json.loads(match.group())

        if not specs:
            specs = [{
                "Brand": f"{prompt[:20]} Systems",
                "Vehicle": "Concept Platform",
                "Country": "EU",
                "Type": "Adaptive",
                "Material": "Context-Based",
                "Strength": "Standard",
                "Website": "N/A"
            }]

        # --------------------------------------
        # DISPLAY
        # --------------------------------------
        st.subheader("🔍 Technical Specs")

        cols = st.columns(3)
        for i, col in enumerate(cols):
            d = specs[i % len(specs)]
            with col:
                st.markdown(f"### {d.get('Brand')}")
                st.write(f"**Vehicle:** {d.get('Vehicle')}")
                for k, v in d.items():
                    if k not in ["Vehicle", "Website"]:
                        st.write(f"**{k}:** {v}")

                if d.get("Website") and d.get("Website") != "N/A":
                    st.link_button("🌐 Visit Website", d.get("Website"))

                if i < len(res.market_photos):
                    st.image(res.market_photos[i]["thumbnail"])

# --------------------------------------
# RENDER
# --------------------------------------
if col2.button("🎨 RENDER"):
    if prompt:
        img = hf_gen_image(f"{prompt}, ultra realistic, 8k")
        if img:
            st.image(img)
            st.session_state.count += 1
