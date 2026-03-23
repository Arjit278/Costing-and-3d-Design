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

# --------------------------------------
# RESULT CONTAINER
# --------------------------------------
class AnalysisResults:
    def __init__(self):
        self.rca_intel = None
        self.specs_raw = None
        self.market_photos = []
        self.ai_concept = None

# --------------------------------------
# API CONFIG (⚠️ Move to secrets later)
# --------------------------------------
OPENROUTER_API_KEY = "YOUR_KEY"
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

MODELS = [
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free"
]

# --------------------------------------
# 🔥 OPENROUTER FIXED ENGINE
# --------------------------------------
def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    for model in MODELS:
        for attempt in range(2):  # retry logic
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    },
                    timeout=40
                )

                if r.status_code == 200:
                    data = r.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content")
                    if content:
                        return content.strip()

            except Exception as e:
                print(f"[ERROR] {model} attempt {attempt}: {e}")

    return None  # important change


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
# THREAD FUNCTIONS (SAFE)
# --------------------------------------
def thread_rca(res, prompt):
    try:
        res.rca_intel = call_openrouter(
            f"""
            Perform CEO-level Root Cause Analysis:
            {prompt}

            Focus:
            - Material science
            - European manufacturing
            - 2026 innovations
            - Engineering logic
            """
        )
    except:
        res.rca_intel = None


def thread_meta(res, prompt):
    try:
        res.specs_raw = call_openrouter(
            f"""
            Return ONLY JSON list of 3 automotive seat cover variations in Europe.

            Keys:
            Brand, Country, Type, Material, Strength

            Topic: {prompt}
            """
        )
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
# 🚀 MAIN EXECUTION (FIXED THREADING)
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

            # ✅ NON-BLOCKING TIMEOUTS
            t1.join(timeout=45)
            t2.join(timeout=25)
            t3.join(timeout=35)

        # --------------------------------------
        # 🧠 SMART RCA FALLBACK
        # --------------------------------------
        if not res.rca_intel:
            res.rca_intel = f"""
Fallback Strategic RCA:

• Hybrid leather (Nappa + Alcantara) dominates EU market  
• Laser perforation for cooling + ventilation  
• Ergonomic stitching (diamond / ribbed)  
• Shift toward sustainable leather processing  
• Modular seat cover customization rising  

(Primary AI engine unavailable)
"""

        st.subheader("📊 RCA")
        st.write(res.rca_intel)

        # --------------------------------------
        # 🎨 IMAGE
        # --------------------------------------
        if res.ai_concept:
            st.image(res.ai_concept)

        # --------------------------------------
        # 🔍 SPEC FIX
        # --------------------------------------
        specs = []
        try:
            match = re.search(r"\[.*\]", str(res.specs_raw), re.DOTALL)
            if match:
                specs = json.loads(match.group())
        except:
            specs = []

        if not specs:
            specs = [
                {"Brand": "Germany Tech", "Country": "Germany", "Type": "Performance", "Material": "Carbon Leather", "Strength": "Industrial"},
                {"Brand": "Italy Lux", "Country": "Italy", "Type": "Luxury", "Material": "Nappa Leather", "Strength": "Premium"},
                {"Brand": "France Eco", "Country": "France", "Type": "Eco", "Material": "Bio Leather", "Strength": "Sustainable"},
            ]

        st.subheader("🔍 Technical Specs")

        cols = st.columns(3)
        for i, col in enumerate(cols):
            d = specs[i % len(specs)]
            with col:
                st.markdown(f"### {d.get('Brand')}")
                for k, v in d.items():
                    st.write(f"**{k}:** {v}")

                if i < len(res.market_photos):
                    st.image(res.market_photos[i]["thumbnail"])

# --------------------------------------
# 🎨 RENDER BUTTON
# --------------------------------------
if col2.button("🎨 RENDER"):
    if prompt:
        img = hf_gen_image(f"{prompt}, ultra realistic, 8k")
        if img:
            st.image(img)
            st.session_state.count += 1
