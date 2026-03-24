import io
import json
import requests
import streamlit as st
import re
import time
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
# API CONFIG
# --------------------------------------
OPENROUTER_API_KEY = "YOUR_KEY"
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free"
]

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
            Generate current automotive trends based on:

            {prompt}

            Requirements:
            - Must match topic exactly
            - No unrelated materials
            - Use correct domain (lighting, seats, electronics etc.)
            - 5 bullet points only
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
            Generate 3 automotive specifications based on:

            {prompt}

            Requirements:
            - Include Vehicle
            - Use correct materials for topic
            - Real brands or OEM suppliers

            Return JSON:
            [
              {{
                "Brand": "",
                "Vehicle": "",
                "Country": "",
                "Type": "",
                "Material": "",
                "Strength": ""
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
        # CURRENT TRENDS (DYNAMIC)
        # --------------------------------------
        if not res.rca_intel:
            st.warning(f"⚠️ Primary Engine Failed: {res.rca_status}")

            # 🔥 dynamic fallback
            res.rca_intel = f"""
Current Trends Insight (Generated Fallback):

• Innovations evolving in: {prompt}
• Material optimization based on component function  
• Increased focus on efficiency and durability  
• Smart integration with electronics and sensors  
• European manufacturing adapting to modular design  
"""

        st.subheader("📊 Current Trends")
        st.write(res.rca_intel)

        # --------------------------------------
        # IMAGE + COUNTER
        # --------------------------------------
        if res.ai_concept:
            st.image(res.ai_concept)
            st.session_state.count += 1

        # --------------------------------------
        # SPECS (FULLY DYNAMIC)
        # --------------------------------------
        specs = []
        try:
            match = re.search(r"\[.*\]", str(res.specs_raw), re.DOTALL)
            if match:
                specs = json.loads(match.group())
        except:
            specs = []

        # 🔥 AI FALLBACK (SECONDARY)
        if not specs:
            try:
                fallback_prompt = f"""
                Generate 3 automotive specs based on:

                {prompt}

                Must match topic exactly.
                Return JSON only.
                """

                ai_specs, _ = call_openrouter(fallback_prompt)

                if ai_specs:
                    match = re.search(r"\[.*\]", ai_specs, re.DOTALL)
                    if match:
                        specs = json.loads(match.group())
            except:
                specs = []

        # 🔥 FINAL SAFE FALLBACK
        if not specs:
            specs = [
                {"Brand": "Generic Auto", "Vehicle": "Concept Model", "Country": "EU", "Type": "Adaptive System", "Material": "Component-specific", "Strength": "Standard"},
                {"Brand": "NextGen Mobility", "Vehicle": "Prototype", "Country": "Germany", "Type": "Smart Module", "Material": "Optimized Material", "Strength": "Balanced"},
                {"Brand": "Future AutoTech", "Vehicle": "Platform X", "Country": "France", "Type": "Integrated System", "Material": "Advanced Composite", "Strength": "High Efficiency"},
            ]

        st.subheader("🔍 Technical Specs")

        cols = st.columns(3)
        for i, col in enumerate(cols):
            d = specs[i % len(specs)]
            with col:
                st.markdown(f"### {d.get('Brand')}")
                st.write(f"**Vehicle:** {d.get('Vehicle')}")
                for k, v in d.items():
                    if k != "Vehicle":
                        st.write(f"**{k}:** {v}")

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
