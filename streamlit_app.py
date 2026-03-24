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
# 🔐 LOGIN SYSTEM (ADDED - NO REMOVAL)
# --------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.title("🔐 Access Panel")

    if not st.session_state.authenticated:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user == "Harmony" and pwd == "Harmony_Pictator123":
                st.session_state.authenticated = True
                st.success("✅ Logged in")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    else:
        st.success("🟢 Logged in as Harmony")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.warning("🔐 Please login from sidebar to continue")
    st.stop()

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
# API CONFIG
# --------------------------------------
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --------------------------------------
# 🌐 WEBSITE FETCH
# --------------------------------------
def fetch_real_website(brand):
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google",
                "q": f"{brand} official website",
                "api_key": SERP_API_KEY
            },
            timeout=5
        )
        results = r.json().get("organic_results", [])
        if results:
            return results[0].get("link")
    except:
        pass

    clean = brand.lower().replace(" ", "").replace("-", "")
    return f"https://www.{clean}.com"

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
        self.final_images = []

# --------------------------------------
# ⚡ FLASHMIND ENGINE
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
                    ],
                    "temperature": 0.2
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
# SAFE JSON
# --------------------------------------
def safe_json_extract(text):
    try:
        match = re.search(r"\[.*\]", str(text), re.DOTALL)
        if match:
            raw = match.group()
            raw = raw.replace("'", '"')
            raw = re.sub(r",\s*}", "}", raw)
            raw = re.sub(r",\s*]", "]", raw)
            return json.loads(raw)
    except:
        pass
    return []

# --------------------------------------
# NORMALIZER
# --------------------------------------
def normalize_specs(specs):
    normalized = []
    for item in specs:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "Brand": item.get("Brand") or item.get("vendor") or "Unknown",
            "Vehicle": item.get("Vehicle") or (item.get("compatibility")[0] if item.get("compatibility") else "Generic"),
            "Type": item.get("Type") or item.get("model") or "Standard",
            "Material": item.get("Material") or ("Synthetic Leather" if "leather" in str(item).lower() else "Advanced"),
            "Strength": item.get("Strength") or "Optimized",
            "Description": item.get("description") or "",
            "Website": item.get("Website") or ""
        })
    return normalized

# --------------------------------------
# IMAGE ENGINE (HF)
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
    res.rca_intel, res.rca_status = call_openrouter_with_fallback_requests(
        f"Generate automotive trends: {prompt}", OPENROUTER_API_KEY
    )

def thread_meta(res, prompt):
    res.specs_raw, _ = call_openrouter_with_fallback_requests(
        f"Generate 3 automotive vendors JSON: {prompt}", OPENROUTER_API_KEY
    )

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
    res.ai_concept = hf_gen_image(prompt)

# --------------------------------------
# UI
# --------------------------------------
prompt = st.text_area("Enter Topic")

col1, col2 = st.columns(2)

if col1.button("🚀 EXECUTE"):
    res = AnalysisResults()

    t1 = threading.Thread(target=thread_rca, args=(res, prompt))
    t2 = threading.Thread(target=thread_meta, args=(res, prompt))
    t3 = threading.Thread(target=thread_assets, args=(res, prompt))

    t1.start(); t2.start(); t3.start()
    t1.join(); t2.join(); t3.join()

    # --------------------------------------
    # 🔥 FINAL IMAGE PIPELINE (FIXED)
    # --------------------------------------
    final_images = []
    if res.market_photos:
        for img_data in res.market_photos:
            url = img_data.get("thumbnail") or img_data.get("original")
            if url:
                final_images.append(url)

    while len(final_images) < 3:
        ai_img = hf_gen_image(f"{prompt}, automotive seat design")
        if ai_img:
            final_images.append(ai_img)
        else:
            break

    while len(final_images) < 3:
        final_images.append(f"https://source.unsplash.com/600x400/?car-seat,{len(final_images)}")

    res.final_images = final_images

    # --------------------------------------
    # DISPLAY
    # --------------------------------------
    st.subheader("📊 Current Trends")
    st.write(res.rca_intel)

    if res.ai_concept:
        st.image(res.ai_concept)
        # --- PATCH: DOWNLOAD CONCEPT ---
        buf_concept = io.BytesIO()
        res.ai_concept.save(buf_concept, format="PNG")
        st.download_button("💾 Save Concept Image", buf_concept.getvalue(), "concept.png", "image/png")

    raw_specs = safe_json_extract(res.specs_raw)
    specs = normalize_specs(raw_specs)

    if not specs:
        retry, _ = call_openrouter_with_fallback_requests(
            f"Generate vendors JSON for {prompt}", OPENROUTER_API_KEY
        )
        specs = normalize_specs(safe_json_extract(retry))

    # --- PATCH: DOWNLOAD TEXT REPORT ---
    report_text = f"ANALYSIS: {prompt}\n\nTRENDS:\n{res.rca_intel}\n\nSPECS:\n{json.dumps(specs, indent=2)}"
    st.sidebar.download_button("📄 Download Full Report", report_text, f"report_{prompt[:10]}.txt", "text/plain")

    st.subheader("🔍 Technical Specs")

    cols = st.columns(3)
    for i, col in enumerate(cols):
        d = specs[i % len(specs)] if specs else {}
        with col:
            brand = d.get("Brand") or f"auto-seat-{i}"
            st.markdown(f"### {brand}")
            st.write(f"**Vehicle:** {d.get('Vehicle')}")
            for k, v in d.items():
                if k not in ["Vehicle", "Website"]:
                    st.write(f"**{k}:** {v}")
            
            if d.get("Description"):
                st.caption(d.get("Description"))

            website = d.get("Website") or fetch_real_website(brand)
            if website:
                st.link_button("🌐 Visit Website", website + f"?ref={i}")

            if i < len(res.final_images):
                img_src = res.final_images[i]
                st.image(img_src)
                # --- PATCH: DOWNLOAD SPEC IMAGE ---
                if isinstance(img_src, Image.Image):
                    buf_spec = io.BytesIO()
                    img_src.save(buf_spec, format="PNG")
                    st.download_button(f"📥 Save {brand} Image", buf_spec.getvalue(), f"{brand}.png", "image/png", key=f"dl_{i}")

# --------------------------------------
# RENDER
# --------------------------------------
if col2.button("🎨 RENDER"):
    img_render = hf_gen_image(f"{prompt}, ultra realistic, 8k")
    if img_render:
        st.image(img_render)
        st.session_state.count += 1
        # --- PATCH: DOWNLOAD RENDER ---
        buf_render = io.BytesIO()
        img_render.save(buf_render, format="PNG")
        st.download_button("🖼️ Save 8K Render", buf_render.getvalue(), "render_8k.png", "image/png")
