import io
import json
import requests
import streamlit as st
import re
import threading
import time
import random
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
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --------------------------------------
# ⚡ FLASHMIND ENGINE (MULTI-MODEL)
# --------------------------------------
ANALYSIS_FALLBACK_MODELS = [
    "openai/gpt-oss-20b:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "x-ai/grok-4.1-fast:free",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_with_fallback_requests(prompt: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for model in ANALYSIS_FALLBACK_MODELS:
        try:
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an automotive engineering expert."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )

            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if content:
                    return content.strip(), "OK"

            elif r.status_code == 429:
                time.sleep(2)

        except:
            continue

    return None, "All models failed"

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
# THREADS (UPDATED)
# --------------------------------------
def thread_rca(res, prompt):
    try:
        output, status = call_openrouter_with_fallback_requests(
            f"""
            Generate current automotive trends for:

            {prompt}

            - Strict domain match
            - Real materials
            - 5 bullet points
            """,
            OPENROUTER_API_KEY
        )
        res.rca_intel = output
        res.rca_status = status
    except Exception as e:
        res.rca_intel = None
        res.rca_status = str(e)


def thread_meta(res, prompt):
    try:
        result, status = call_openrouter_with_fallback_requests(
            f"""
            Generate 3 REAL automotive vendors for:

            {prompt}

            Include:
            - Brand
            - Vehicle
            - Material (match prompt)
            - Website

            Return JSON
            """,
            OPENROUTER_API_KEY
        )
        res.specs_raw = result
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

            t1.join(timeout=40)
            t2.join(timeout=25)
            t3.join(timeout=30)

        # --------------------------------------
        # CURRENT TRENDS
        # --------------------------------------
        if not res.rca_intel:
            st.warning(f"⚠️ Primary Engine Failed: {res.rca_status}")

            trend_output, _ = call_openrouter_with_fallback_requests(
                f"Generate trends for: {prompt}",
                OPENROUTER_API_KEY
            )

            res.rca_intel = trend_output or "No trends available"

        st.subheader("📊 Current Trends")
        st.write(res.rca_intel)

        # --------------------------------------
        # IMAGE
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

        if not specs:
            ai_specs, _ = call_openrouter_with_fallback_requests(
                f"Generate vendors for: {prompt} JSON",
                OPENROUTER_API_KEY
            )

            if ai_specs:
                match = re.search(r"\[.*\]", ai_specs, re.DOTALL)
                if match:
                    specs = json.loads(match.group())

        if not specs:
            specs = [{"Brand": "Fallback System", "Vehicle": "Concept", "Material": "Synthetic"}]

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

                if d.get("Website"):
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
