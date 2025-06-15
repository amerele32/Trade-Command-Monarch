import streamlit as st
import json
import os

st.set_page_config(layout="wide", page_title="Trade Command Monarch", page_icon=":robot_face:", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        body { background-color: #14161a; }
        .stButton>button { border-radius: 16px; }
    </style>
""", unsafe_allow_html=True)

# File paths
STOP_FILE = "stop_bots.json"
CONFIDENCE_FILE = "confidence.json"

def set_stop_flag(value: bool):
    with open(STOP_FILE, "w") as f:
        json.dump({"stop": value}, f)

def get_stop_flag():
    if not os.path.exists(STOP_FILE):
        return False
    with open(STOP_FILE, "r") as f:
        return json.load(f).get("stop", False)

def set_confidence(val: int):
    with open(CONFIDENCE_FILE, "w") as f:
        json.dump({"confidence": val}, f)

def get_confidence():
    if not os.path.exists(CONFIDENCE_FILE):
        set_confidence(85)
    with open(CONFIDENCE_FILE, "r") as f:
        return json.load(f).get("confidence", 85)

# Sidebar controls
st.title("💎 Trade Command Monarch Dashboard")
st.markdown("### 💰 Balance\n\n£500.00")

st.divider()

st.header("🔧 Controls")
confidence = st.slider(
    "Global Confidence % to Take Trade", min_value=50, max_value=100,
    value=get_confidence(), step=1, help="Set minimum confidence for bots to trade."
)
if confidence != get_confidence():
    set_confidence(confidence)
    st.success(f"Set confidence to {confidence}%")

allow_anytime = st.toggle("⚡ Allow Bots To Trade Outside Market Hours", value=False)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🟢 Start All Bots"):
        set_stop_flag(False)
        st.success("Bots STARTED! (Launch them from terminal)")
with col2:
    if st.button("🔴 Stop All Bots"):
        set_stop_flag(True)
        st.warning("Bots stopped! (This will signal bots to stop and send you an email)")

st.info("To make these controls work, overwrite all bot scripts as shown below!")

# Status section (dummy for now; bots will update this as you extend)
st.divider()
st.header("🤖 Bot Status & Last Heartbeat")
for bot in ["Momentum", "Wick", "Trend"]:
    st.markdown(f"**{bot}** — Last heartbeat: _(add logic to show actual time)_")

st.divider()
st.button("🔄 Refresh")
