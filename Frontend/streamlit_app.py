import streamlit as st
import requests

# ================================
# CONFIG
# ================================
API_BASE_URL = "https://voyage-analytics-srf9.onrender.com"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"

st.set_page_config(
    page_title="Voyage Analytics – Flight Price Prediction",
    page_icon="✈️",
    layout="centered"
)

# ================================
# UI
# ================================
st.title("✈️ Flight Price Prediction")
st.write("Predict flight prices using our ML-powered analytics engine.")

st.divider()

distance = st.number_input(
    "Distance (in km)",
    min_value=50,
    max_value=10000,
    value=1200,
    step=50
)

flight_type = st.selectbox(
    "Flight Type",
    ["economy", "business", "firstClass", "premium"]
)

agency = st.selectbox(
    "Agency",
    ["CloudNine", "FlyingDrops", "Rainbow"]
)

st.divider()

# ================================
# ACTION
# ================================
if st.button("Predict Flight Price 🚀"):
    payload = {
        "distance": distance,
        "flightType": flight_type,
        "agency": agency
    }

    try:
        with st.spinner("Calling prediction API..."):
            response = requests.post(
                PREDICT_ENDPOINT,
                json=payload,
                timeout=20
            )

        if response.status_code == 200:
            result = response.json()

            if "predicted_price" in result:
                st.success(
                    f"💰 Estimated Flight Price: ₹ {result['predicted_price']}"
                )
            else:
                st.error("Unexpected API response format.")
                st.json(result)

        else:
            st.error("API returned an error.")
            try:
                st.json(response.json())
            except Exception:
                st.text(response.text)

    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API.")

    except Exception as e:
        st.error(f"Unexpected error: {e}")
