import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(
    page_title="Voyage Analytics Pro",
    page_icon="✈️",
    layout="wide"
)

# Replace with your actual Render or Local URL
BACKEND_URL = "https://voyage-analytics-r34b.onrender.com"

# ================= PREMIUM UI DESIGN (CSS) =================
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

    /* Ultra Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        border-radius: 25px;
        margin-bottom: 25px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }

    /* Custom Input Styles */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-radius: 10px !important;
    }

    h1, h2, h3, p, label { color: white !important; font-family: 'Inter', sans-serif; }
    
    .welcome-text {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "flight_price" not in st.session_state:
    st.session_state.flight_price = 0

# ================= LANDING / NAME ENTRY =================
if not st.session_state.user_name:
    st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<h1 class="welcome-text">VOYAGE</h1>', unsafe_allow_html=True)
        st.write("Welcome to the future of travel planning.")
        name_input = st.text_input("Enter your name to begin:", placeholder="Ex: John Doe")
        if st.button("Start Planning ✈️"):
            if name_input:
                st.session_state.user_name = name_input
                st.rerun()
            else:
                st.warning("Please enter a name.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= MAIN DASHBOARD =================

# Header with dynamic name
st.markdown(f'<p class="welcome-text">Welcome, {st.session_state.user_name}!</p>', unsafe_allow_html=True)
st.write(f"Today is {datetime.now().strftime('%A, %d %B %Y')}")

# Sidebar History
st.sidebar.title("📜 Booking History")
if st.session_state.history:
    for h in reversed(st.session_state.history):
        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 3px solid #00c6ff;">
            <small>{h['from']} ➜ {h['to']}<br><b>₹ {h['price']}</b></small>
        </div>
        """, unsafe_allow_html=True)
else:
    st.sidebar.info("No bookings yet.")

if st.sidebar.button("Switch User"):
    st.session_state.user_name = ""
    st.rerun()

# --- MAIN TABS ---
tab1, tab2 = st.tabs(["🎫 Flight Prediction", "🏨 Hotel & Trip Budget"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Flight Search")
    
    # Logic for City Selection
    if 'from_city' not in st.session_state: st.session_state.from_city = "Sao Paulo (SP)"
    if 'to_city' not in st.session_state: st.session_state.to_city = "Salvador (BH)"

    def swap():
        st.session_state.from_city, st.session_state.to_city = st.session_state.to_city, st.session_state.from_city

    c1, c_mid, c2 = st.columns([4, 1, 4])
    cities = ["Sao Paulo (SP)", "Salvador (BH)", "Natal (RN)", "Recife (PE)", "Florianopolis (SC)", "Aracaju (SE)"]
    
    with c1: st.selectbox("Departure", cities, key="from_city")
    with c_mid: 
        st.markdown("<br>", unsafe_allow_html=True); st.button("🔄", on_click=swap)
    with c2: st.selectbox("Destination", cities, key="to_city")

    col_a, col_b = st.columns(2)
    with col_a:
        travel_date = st.date_input("Travel Date", datetime.now())
        agency = st.selectbox("Agency", ["Cloud Jet", "Sky High", "Voyage Air", "Star Travel"])
    with col_b:
        f_class = st.radio("Cabin Class", ["Economy", "Business"], horizontal=True)
        pop = st.slider("Route Popularity", 0, 100, 50)

    if st.button("Calculate Best Price"):
        # Logic matches your app (1).py payload requirements
        payload = {
            "date": str(travel_date),
            "from_city": st.session_state.from_city,
            "to_city": st.session_state.to_city,
            "agency": agency,
            "class": f_class,
            "popularity": pop
        }
        
        try:
            res = requests.post(f"{BACKEND_URL}/predict", json=payload)
            if res.status_code == 200:
                price = res.json()['predicted_price']
                st.session_state.flight_price = price
                # Add to history
                st.session_state.history.append({"from": st.session_state.from_city, "to": st.session_state.to_city, "price": price})
                
                st.balloons()
                st.markdown(f"""
                <div style="text-align: center; background: rgba(0, 198, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #00c6ff;">
                    <h2 style="margin:0;">Predicted Fare: ₹ {price:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.error("Could not connect to the Backend API.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Hotel & Total Budget Analysis")
    
    h1, h2, h3 = st.columns(3)
    with h1: dest = st.selectbox("Hotel Location", cities)
    with h2: nights = st.number_input("Nights", 1, 30, 3)
    with h3: budget = st.number_input("Total Trip Budget (₹)", 1000, 100000, 20000)

    if st.button("🏨 Search Hotels"):
        f_price = st.session_state.flight_price
        try:
            # Matches your app (1).py recommend-hotels logic
            res = requests.post(f"{BACKEND_URL}/recommend-hotels", json={"place": dest, "days": nights})
            hotels = res.json().get("recommended_hotels", [])
            
            for h in hotels:
                total_stay = h['calculated_total']
                total_trip = total_stay + f_price
                is_ok = total_trip <= budget
                
                color = "#00ffcc" if is_ok else "#ff4b4b"
                
                st.markdown(f"""
                <div class="glass-card" style="border-left: 5px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin:0;">{h['name']}</h4>
                        <span style="background: {color}; color: black; padding: 2px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">
                            {'WITHIN BUDGET' if is_ok else 'OVER BUDGET'}
                        </span>
                    </div>
                    <p style="margin: 10px 0 5px 0;">Nightly: ₹ {h['price']} | Total Stay: ₹ {total_stay}</p>
                    <h3 style="margin:0; color: {color} !important;">Total Trip: ₹ {total_trip:,.2f}</h3>
                    <small style="opacity: 0.6;">(Includes Flight + Hotel)</small>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.error("Error fetching hotel data.")
    st.markdown('</div>', unsafe_allow_html=True)
