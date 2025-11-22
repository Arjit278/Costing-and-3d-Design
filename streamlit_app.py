import io
import base64
import requests
import streamlit as st
from PIL import Image
from datetime import datetime

# --------------------------------------
# 🔧 PAGE CONFIG + DARK THEME + LOGO
# --------------------------------------
st.set_page_config(
    page_title="Pictator Creator",
    page_icon="⚙️",
    layout="wide",
)

st.markdown(
    """
    <h1 style='text-align:center;color:#00eaff;font-size:45px;'>
        ⚙️ Pictator Creator – HF Router Edition
    </h1>
    <h3 style='text-align:center;color:#ffffff;'>Multi-User | Admin Panel | Streamlit Cloud</h3>
    <hr style='border:1px solid #333'>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# 🔵 GLOBAL USAGE TRACKER (PERSISTENT ON STREAMLIT CLOUD)
# =====================================================================
@st.cache_resource
def init_usage_store():
    return {
        "total": 0,
        "users": {}  # username → {"count": X, "last": timestamp}
    }

usage_store = init_usage_store()

def update_usage(username):
    usage_store["total"] += 1

    if username not in usage_store["users"]:
        usage_store["users"][username] = {"count": 0, "last": None}

    usage_store["users"][username]["count"] += 1
    usage_store["users"][username]["last"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =====================================================================
# 🔐 USERS LOADED FROM STREAMLIT SECRETS (PERSISTENT)
# =====================================================================
if "users" not in st.session_state:
    st.session_state.users = dict(st.secrets.get("users", {}))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")
HF_TOKEN_SECRET = st.secrets.get("HF_TOKEN", "")

# --------------------------------------
# SIDEBAR LOGIN / LOGOUT
# --------------------------------------
st.sidebar.title("🔐 Login Panel")

if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as: {st.session_state.current_user}")

    user = st.session_state.current_user
    if user in usage_store["users"]:
        st.sidebar.info(
            f"Your Usage Count: **{usage_store['users'][user]['count']}**"
        )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

else:
    st.sidebar.subheader("User Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid Username or Password")

# --------------------------------------
# 🔐 ADMIN PANEL (SIDEBAR)
# --------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🛠 Admin Access")

admin_pass = st.sidebar.text_input("Admin Password", type="password")

if admin_pass == ADMIN_PASSWORD:
    st.sidebar.success("Admin Verified ✔")

    st.sidebar.markdown("### ➕ Add User")
    new_user = st.sidebar.text_input("New Username")
    new_pass = st.sidebar.text_input("New Password")

    if st.sidebar.button("Add User"):
        if new_user.strip() == "":
            st.sidebar.error("Username required")
        else:
            st.session_state.users[new_user] = new_pass
            st.sidebar.success(f"User '{new_user}' added")

    st.sidebar.markdown("### ❌ Delete User")
    del_user = st.sidebar.selectbox("Select user", list(st.session_state.users.keys()))
    if st.sidebar.button("Delete User"):
        del st.session_state.users[del_user]
        st.sidebar.success(f"User '{del_user}' deleted")

    st.sidebar.markdown("### 👥 Current Users (Editable JSON)")
    st.sidebar.json(st.session_state.users)

    st.sidebar.markdown("### 📌 Paste this back into Streamlit Secrets")
    st.sidebar.code(
        "[users]\n" +
        "\n".join([f"{u}=\"{p}\"" for u, p in st.session_state.users.items()])
    )

    # -------------------------
    # 📊 USAGE STATISTICS
    # -------------------------
    st.sidebar.markdown("### 📊 Usage Statistics")
    st.sidebar.info(f"Total Generations: **{usage_store['total']}**")

    for u, data in usage_store["users"].items():
        st.sidebar.write(
            f"**{u}** → {data['count']} (Last: {data['last']})"
        )

else:
    st.sidebar.info("Admin panel locked")

# --------------------------------------
# STOP if not logged in
# --------------------------------------
if not st.session_state.logged_in:
    st.warning("🔑 Please login to access Pictator Creator.")
    st.stop()

# =====================================================================
# 🎨 HF ROUTER IMAGE GENERATOR ENGINE
# =====================================================================

HF_TOKEN = HF_TOKEN_SECRET
HF_ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

def hf_router_generate_image(model_repo: str, prompt: str, hf_token: str,
                             width=1024, height=1024, steps=30, guidance=3.5):

    if not hf_token:
        return {"type": "error", "data": "[HF_TOKEN missing]"}

    url = f"{HF_ROUTER_BASE}/{model_repo}"
    headers = {"Authorization": f"Bearer {hf_token}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": steps,
            "guidance_scale": guidance
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
    except Exception as e:
        return {"type": "error", "data": f"[HF Router request failed: {e}]"}

    # Direct Image
    if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
        try:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            return {"type": "image", "data": img}
        except Exception as e:
            return {"type": "error", "data": f"[HF decode failed: {e}]"}

    # JSON fallback
    try:
        data = resp.json()
    except:
        return {"type": "error", "data": resp.text[:400]}

    try:
        if "generated_image" in data:
            img_bytes = base64.b64decode(data["generated_image"])
            return {"type": "image", "data": Image.open(io.BytesIO(img_bytes)).convert("RGB")}

        if "images" in data:
            img_bytes = base64.b64decode(data["images"][0])
            return {"type": "image", "data": Image.open(io.BytesIO(img_bytes)).convert("RGB")}
    except Exception as e:
        return {"type": "error", "data": f"[HF parse error: {e}]"}

    return {"type": "error", "data": f"Unsupported response: {data}"}

# =====================================================================
# UI – Pictator Creator
# =====================================================================

st.title("🎨 Pictator Creator (HF Router Only)")

st.subheader("Create Engineering Drawing using HF Router Models")

MODELS = {
    "Sketchers (Lineart / Mechanical)": "black-forest-labs/FLUX.1-dev",
    "CAD Drawing XL (2D CNC Blueprints)": "stabilityai/stable-diffusion-xl-base-1.0",
    "RealisticVision (3D)": "stabilityai/stable-diffusion-3-medium-diffusers",
}

model_choice = st.selectbox("Model", list(MODELS.keys()))

prompt = st.text_area(
    "Prompt",
    "technical CNC blueprint, mechanical disc brake, top view, thin black engineering lineart"
)

col1, col2 = st.columns(2)
with col1:
    width = st.number_input("Width", 256, 1536, 768)
with col2:
    height = st.number_input("Height", 256, 1536, 768)

steps = st.slider("Inference Steps", 5, 80, 30)
guidance = st.slider("Guidance Scale", 1.0, 12.0, 3.5)

if st.button("Generate"):
    with st.spinner("Generating image from HuggingFace Router..."):
        repo = MODELS[model_choice]
        out = hf_router_generate_image(
            repo, prompt, HF_TOKEN,
            width=width, height=height,
            steps=steps, guidance=guidance
        )

    # ---------------------------------
    # 🔵 UPDATE USER USAGE COUNTER
    # ---------------------------------
    update_usage(st.session_state.current_user)

    if out["type"] == "image":
        img = out["data"]
        st.image(img, caption="Generated Drawing", use_column_width=True)

        buf = io.BytesIO()
        img.save(buf, "PNG")
        st.download_button("Download PNG", buf.getvalue(), "pictator.png")
    else:
        st.error(out["data"])
