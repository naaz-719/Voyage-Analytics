import streamlit as st
import pandas as pd
import requests
import joblib
import os
import altair as alt
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(
    page_title="Voyage Analytics Pro",
    page_icon="✈️",
    layout="wide"
)

BACKEND_URL = "https://voyage-analytics-r34b.onrender.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= PREMIUM ANIMATED DESIGN =================
st.markdown("""
<style>
    /* Animated Dynamic Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white !important;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Professional Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .metric-box {
        background: rgba(0, 198, 255, 0.1);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(0, 198, 255, 0.3);
    }

    /* Target all text elements to ensure they are white */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stSelectbox label, .stNumberInput label {
        color: white !important;
    }

    .welcome-text {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE (Updated for First Name) =================
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "flight_price" not in st.session_state:
    st.session_state.flight_price = 0

if "destination" not in st.session_state:
    st.session_state.destination = None

# ================= WELCOME SCREEN (Replaces Login Logic) =================
if not st.session_state.user_name:
    st.markdown('<div style="height: 20vh;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<h1 class="welcome-text">VOYAGE</h1>', unsafe_allow_html=True)
        st.write("Plan your next journey with AI.")
        name_input = st.text_input("Enter your First Name to begin:")
        if st.button("Access Dashboard ✈️"):
            if name_input:
                st.session_state.user_name = name_input
                st.rerun()
            else:
                st.error("Please enter your name!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= LOAD FEATURE NAMES (Logic from your file) =================
@st.cache_resource
def load_features():
    return joblib.load(os.path.join(BASE_DIR, "feature_names.pkl"))

feature_names = load_features()

from_options = sorted([c.replace("from_", "") for c in feature_names if c.startswith("from_")])
to_options = sorted([c.replace("to_", "") for c in feature_names if c.startswith("to_")])
agency_options = sorted([c.replace("agency_", "") for c in feature_names if c.startswith("agency_")])
flight_type_options = sorted([c.replace("flightType_", "") for c in feature_names if c.startswith("flightType_")])

DISTANCE_MAP = {
    ("Recife (PE)", "Brasilia (DF)"): 1650,
    ("Recife (PE)", "Sao Paulo (SP)"): 2120,
    ("Recife (PE)", "Rio de Janeiro (RJ)"): 2330,
    ("Natal (RN)", "Sao Paulo (SP)"): 2940,
    ("Florianopolis (SC)", "Sao Paulo (SP)"): 705,
}

def get_distance(frm, to):
    return DISTANCE_MAP.get((frm, to)) or DISTANCE_MAP.get((to, frm)) or 1000

# ================= MAIN UI =================
st.markdown(f'<p class="welcome-text">Welcome, {st.session_state.user_name}</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✈️ Flight Planning", "🏨 Hotel Planning"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if "from_city" not in st.session_state: st.session_state.from_city = from_options[0]
    if "to_city" not in st.session_state: st.session_state.to_city = to_options[1]

    col1, col2, col3 = st.columns([4,1,4])
    with col1:
        st.session_state.from_city = st.selectbox("From", from_options, index=from_options.index(st.session_state.from_city))
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄"):
            st.session_state.from_city, st.session_state.to_city = st.session_state.to_city, st.session_state.from_city
            st.rerun()
    with col3:
        filtered_to = [c for c in to_options if c != st.session_state.from_city]
        if st.session_state.to_city not in filtered_to: st.session_state.to_city = filtered_to[0]
        st.session_state.to_city = st.selectbox("To", filtered_to, index=filtered_to.index(st.session_state.to_city))

    travel_date = st.date_input("Travel Date", datetime.today())
    agency = st.selectbox("Agency", agency_options)
    flight_type = st.selectbox("Flight Type", flight_type_options)
    distance = get_distance(st.session_state.from_city, st.session_state.to_city)

    if st.button("💰 Predict Flight Price"):
        payload = {
            "from": st.session_state.from_city, "to": st.session_state.to_city,
            "agency": agency, "flightType": flight_type, "distance": distance,
            "day": travel_date.day, "month": travel_date.month, "year": travel_date.year
        }
        res = requests.post(f"{BACKEND_URL}/predict-flight", json=payload)
        if res.status_code == 200:
            price = res.json()["predicted_price"]
            st.session_state.flight_price, st.session_state.destination = price, st.session_state.to_city
            st.markdown(f'<div class="metric-box"><h2>Estimated Fare</h2><h1>$ {price}</h1></div>', unsafe_allow_html=True)
            st.session_state.history.append({"from": st.session_state.from_city, "to": st.session_state.to_city, "price": price})
        else:
            st.error(res.json())
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    place = st.session_state.destination if st.session_state.destination else st.text_input("Destination City")
    if st.session_state.destination: st.info(f"Destination detected: {place}")
    
    h1, h2 = st.columns(2)
    with h1: days = st.number_input("Stay Duration", 1, 30, 2)
    with h2: max_total = st.number_input("Total Budget", 1000, 200000, 20000)

    if st.button("🏨 Find Hotels"):
        res = requests.post(f"{BACKEND_URL}/recommend-hotels", json={"place": place, "days": days, "max_total": max_total})
        if res.status_code == 200:
            hotels = res.json()["recommended_hotels"]
            for hotel in hotels:
                total_trip = hotel["calculated_total"] + st.session_state.flight_price
                status = "✅ Within Budget" if total_trip <= max_total else "❌ Over Budget"
                st.markdown(f"""
                <div class="glass-card" style="border-left: 5px solid {'#00ffcc' if total_trip <= max_total else '#ff4b4b'};">
                    <h3>{hotel['name']}</h3>
                    <p>Price/Night: $ {hotel['price']} | Stay: $ {hotel['calculated_total']}</p>
                    <h4>Total Trip [Flight + Hotel]: $ {total_trip}</h4>
                    <p><b>{status}</b></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(res.json())
    st.markdown('</div>', unsafe_allow_html=True)

# ================= SIDEBAR HISTORY =================
st.sidebar.title("📜 Trip History")
if st.session_state.history:
    for h in reversed(st.session_state.history):
        st.sidebar.markdown(f'<div style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1);">{h["from"]} ➜ {h["to"]} | <b>$ {h["price"]}</b></div>', unsafe_allow_html=True)

if st.sidebar.button("Switch User"):
    st.session_state.clear()
    st.rerun()
