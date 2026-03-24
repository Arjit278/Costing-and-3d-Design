import io
import json
import requests
import streamlit as st
import re
import threading
import time
import random
import zipfile
from io import BytesIO
from PIL import Image

# --------------------------------------
# 🔐 LOGIN SYSTEM (UNCHANGED)
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
# PAGE CONFIG
# --------------------------------------
st.set_page_config(page_title="Pictator Pro", page_icon="🏎️", layout="wide")

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# SESSION COUNTER
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
            params={"engine": "google", "q": f"{brand} official website", "api_key": SERP_API_KEY},
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
# 📦 DOWNLOAD PACKAGE (ADDED)
# --------------------------------------
def create_download_package(prompt, trends, specs, images):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:

        # TEXT
        text = f"Prompt:\n{prompt}\n\nTrends:\n{trends}\n\nSpecs:\n\n"
        for i, s in enumerate(specs):
            text += f"{i+1}. {s.get('Brand')}\n"
            for k, v in s.items():
                text += f"{k}: {v}\n"
            text += "\n"

        zf.writestr("report.txt", text)

        # IMAGES
        for i, img in enumerate(images):
            try:
                if isinstance(img, str):
                    r = requests.get(img, timeout=10)
                    zf.writestr(f"image_{i+1}.jpg", r.content)
                else:
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    zf.writestr(f"image_{i+1}.jpg", buf.getvalue())
            except:
                pass

    zip_buffer.seek(0)
    return zip_buffer

# --------------------------------------
# RESULT CLASS
# --------------------------------------
class AnalysisResults:
    def __init__(self):
        self.rca_intel = None
        self.specs_raw = None
        self.market_photos = []
        self.ai_concept = None
        self.rca_status = "OK"

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
        if isinstance(item, dict):
            normalized.append({
                "Brand": item.get("Brand") or item.get("vendor") or "Unknown",
                "Vehicle": item.get("Vehicle") or "Generic",
                "Type": item.get("Type") or "Standard",
                "Material": item.get("Material") or "Synthetic Leather",
                "Strength": item.get("Strength") or "Optimized",
                "Description": item.get("description") or "",
                "Website": item.get("Website") or ""
            })
    return normalized

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
# OPENROUTER CALL
# --------------------------------------
def call_openrouter_with_fallback_requests(prompt, api_key):
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "openai/gpt-oss-20b:free",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        return r.json()["choices"][0]["message"]["content"], "OK"
    except:
        return None, "Fail"

# --------------------------------------
# THREADS
# --------------------------------------
class Res:
    pass

def thread_data(res, prompt):
    res.trend, _ = call_openrouter_with_fallback_requests(prompt, OPENROUTER_API_KEY)
    res.specs = call_openrouter_with_fallback_requests(
        f"Generate 3 vendors JSON: {prompt}", OPENROUTER_API_KEY
    )[0]

def thread_images(res, prompt):
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={"engine": "google_images", "q": prompt, "api_key": SERP_API_KEY}
        )
        res.images = r.json().get("images_results", [])
    except:
        res.images = []

# --------------------------------------
# UI
# --------------------------------------
prompt = st.text_area("Enter Topic")

col1, col2 = st.columns(2)

if col1.button("🚀 EXECUTE"):
    res = Res()

    t1 = threading.Thread(target=thread_data, args=(res, prompt))
    t2 = threading.Thread(target=thread_images, args=(res, prompt))

    t1.start(); t2.start()
    t1.join(); t2.join()

    # IMAGE PIPELINE
    final_images = []

    if res.images:
        for i in res.images[:3]:
            url = i.get("thumbnail") or i.get("original")
            if url:
                final_images.append(url)

    while len(final_images) < 3:
        img = hf_gen_image(prompt)
        if img:
            final_images.append(img)
        else:
            break

    while len(final_images) < 3:
        final_images.append(f"https://source.unsplash.com/600x400/?car-seat,{len(final_images)}")

    # 🔥 COUNTER FIX (ADDED)
    st.session_state.count += len(final_images)

    # DISPLAY
    st.subheader("📊 Current Trends")
    st.write(res.trend)

    specs = normalize_specs(safe_json_extract(res.specs))

    st.subheader("🔍 Technical Specs")

    cols = st.columns(3)
    for i, col in enumerate(cols):
        d = specs[i % len(specs)] if specs else {}

        with col:
            brand = d.get("Brand", f"auto-{i}")
            st.markdown(f"### {brand}")

            if i < len(final_images):
                st.image(final_images[i])

            st.write(f"Vehicle: {d.get('Vehicle')}")
            st.write(f"Material: {d.get('Material')}")

            if d.get("Description"):
                st.caption(d.get("Description"))

            website = fetch_real_website(brand)
            st.link_button("🌐 Visit Website", website + f"?ref={i}")

    # 🔥 DOWNLOAD BUTTON (ADDED)
    zip_data = create_download_package(prompt, res.trend, specs, final_images)

    st.download_button(
        "📥 Download Full Report",
        data=zip_data,
        file_name="pictator_report.zip",
        mime="application/zip"
    )

# --------------------------------------
# RENDER
# --------------------------------------
if col2.button("🎨 RENDER"):
    img = hf_gen_image(f"{prompt}, ultra realistic, 8k")
    if img:
        st.image(img)
