import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

API_URL = "http://13.60.230.195:8080/predict"

st.set_page_config(page_title="Insurance Predictor", layout="centered", page_icon="💡")
st.title("💼 Insurance Premium Category Predictor")

# Optional: Lottie animation (insurance theme)
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_insurance = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_ygiuluqn.json")

with st.container():
    left_col, right_col = st.columns([1.5, 2])
    with left_col:
        st_lottie(lottie_insurance, height=200, key="insurance_anim")
    with right_col:
        st.markdown("Enter your details below to predict your insurance premium category.")
        st.markdown("⬇️")

# Input form
with st.form("predict_form"):
    st.subheader("🔍 Personal & Lifestyle Information")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("🎂 Age", min_value=1, max_value=119, value=30)
        weight = st.number_input("⚖️ Weight (kg)", min_value=1.0, value=65.0)
        height_m = st.number_input("📏 Height (meters)", min_value=0.5, max_value=2.5, value=1.7)
    with col2:
        income_lpa = st.number_input("💵 Annual Income (LPA)", min_value=0.1, value=10.0)
        smoker = st.selectbox("🚬 Do you smoke?", options=[True, False])
        city = st.text_input("🏙️ City", value="Mumbai")
        occupation = st.selectbox(
            "💼 Occupation",
            ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job']
        )

    submit = st.form_submit_button("🔮 Predict My Premium Category")

if submit:
    # Convert height to centimeters
    height_cm = round(height_m * 100, 1)

    # Calculate BMI and lifestyle risk client-side
    bmi = round(weight / (height_m ** 2), 2)
    risk = (
        "High" if smoker and bmi > 30 else
        "Medium" if smoker or bmi > 27 else
        "Low"
    )

    st.markdown("---")
    st.subheader("📊 Your Health Snapshot:")
    st.write(f"🧮 **BMI:** {bmi}")
    st.write(f"⚠️ **Lifestyle Risk:** {risk}")

    input_data = {
        "age": age,
        "weight": weight,
        "height": height_cm,
        "income_lpa": income_lpa,
        "smoker": str(smoker),  # FastAPI expects "True"/"False" as strings
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data)
        result = response.json()

        if response.status_code == 200 and "predicted_category" in result:
            prediction = result["predicted_category"]
            st.success(f"✅ **Predicted Insurance Premium Category:** `{prediction}`")
        else:
            st.error("⚠️ Unexpected response from server.")
            st.json(result)

    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the FastAPI backend. Is it running at `localhost:8000`?")
