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

# ================= NEW PREMIUM DESIGN (ONLY BG & GLASS CHANGES) =================
st.markdown("""
<style>
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Upgraded Glass Card */
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
    
    h1, h2, h3, p, label, .stMarkdown {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
# We replaced 'logged_in' logic with your 'First Name' request
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "flight_price" not in st.session_state:
    st.session_state.flight_price = 0

# ================= WELCOME SCREEN (REPLACES LOGIN) =================
if not st.session_state.user_name:
    st.markdown('<div style="height: 20vh;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.title("✈️ Welcome to Voyage")
        name = st.text_input("Please enter your First Name to continue:")
        if st.button("Enter Dashboard"):
            if name:
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Please enter a name!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= MAIN APP LOGIC (NO CHANGES TO LOGIC) =================
st.title(f"🚀 Welcome, {st.session_state.user_name}!")

tab1, tab2 = st.tabs(["🎫 Flight Prediction", "🏨 Hotel Recommendation"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Predict Flight Price")
    
    col1, col2 = st.columns(2)
    with col1:
        distance = st.number_input("Distance", value=1000)
        agency = st.selectbox("Agency", [0, 1, 2, 3])
        flight_type = st.selectbox("Flight Type", [0, 1])
    with col2:
        day = st.slider("Day", 1, 31, 15)
        is_weekend = st.selectbox("Is Weekend", [0, 1])
        popularity = st.number_input("Route Popularity", value=50)

    if st.button("Predict Price"):
        payload = {
            "distance": distance,
            "agency": agency,
            "flightType": flight_type,
            "day": day,
            "is_weekend": is_weekend,
            "route_popularity": popularity
        }
        res = requests.post(f"{BACKEND_URL}/predict", json=payload)
        if res.status_code == 200:
            price = res.json()["predicted_price"]
            st.session_state.flight_price = price
            st.session_state.history.append({"from": "Origin", "to": "Destination", "price": price})
            st.success(f"Predicted Price: ₹ {price}")
        else:
            st.error("Error in prediction")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Find Hotels")
    
    h1, h2, h3 = st.columns(3)
    with h1: place = st.selectbox("Place", ["Florianopolis (SC)", "Salvador (BH)", "Natal (RN)", "Aracaju (SE)", "Recife (PE)", "Sao Paulo (SP)"])
    with h2: days = st.number_input("Days", min_value=1, value=1)
    with h3: max_total = st.number_input("Budget", value=20000)

    if st.button("🏨 Find Hotels"):
        payload = {"place": place, "days": days, "max_total": max_total}
        res = requests.post(f"{BACKEND_URL}/recommend-hotels", json=payload)
        if res.status_code == 200:
            hotels = res.json()["recommended_hotels"]
            for hotel in hotels:
                total_trip = hotel["calculated_total"] + st.session_state.flight_price
                status = "✅ Within Budget" if total_trip <= max_total else "❌ Over Budget"
                st.markdown(f"""
                <div class="glass-card">
                    <h3>{hotel['name']}</h3>
                    <p>Price per Night: ₹ {hotel['price']}</p>
                    <p><b>Total Trip Cost: ₹ {total_trip}</b></p>
                    <p>{status}</p>
                </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📜 History")
for h in reversed(st.session_state.history):
    st.sidebar.write(f"Flight: ₹ {h['price']}")

if st.sidebar.button("Switch User"):
    st.session_state.user_name = ""
    st.rerun()
