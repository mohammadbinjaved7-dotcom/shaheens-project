import streamlit as st
import pandas as pd
 
import main
 
st.set_page_config(page_title="Astronaut Health Monitor", layout="wide")
 
STATUS_COLOR = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}
 
st.title("🧑‍🚀 Astronaut Health Monitor")
st.caption("Live health indicators. Flags issues before they become emergencies.")
 
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["time", "heart_rate", "bone_density_loss", "radiation_dose", "sleep_hours"]
    )
if "profile" not in st.session_state:
    st.session_state.profile = None
 
col1, col2 = st.columns([1, 3])
 
with col1:
    st.subheader("Astronaut Profile")
 
    if st.session_state.profile is None:
        with st.form("profile_form"):
            name = st.text_input("Name", "Mb. J")
            age = st.number_input("Age", 18, 70, 40)
            sex = st.selectbox("Sex", ["M", "F"])
            weight = st.number_input("Weight (kg)", 40, 150, 78)
            height = st.number_input("Height (cm)", 140, 220, 180)
            activity = st.selectbox("Activity level", ["low", "moderate", "high"])
            submitted = st.form_submit_button("Create profile")
            if submitted:
                st.session_state.profile = main.new_profile(
                    name, age, sex, weight, height, activity
                )
    else:
        p = st.session_state.profile
        st.write(f"**{p['name']}**")
        st.write(f"{p['age']}y, {p['weight_kg']}kg, {p['height_cm']}cm")
        calories = main.calculate_calories(p)
        st.metric("Recommended daily intake", f"{calories} kcal")
 
        if st.button("Take reading"):
            reading = main.get_latest_reading()
            row = {"time": len(st.session_state.history), **reading}
            st.session_state.history = pd.concat(
                [st.session_state.history, pd.DataFrame([row])], ignore_index=True
            )
 
        if st.button("Reset profile"):
            st.session_state.profile = None
 
with col2:
    if not st.session_state.history.empty:
        latest = st.session_state.history.iloc[-1]
        metric_cols = st.columns(4)
        labels = {
            "heart_rate": ("Heart Rate", "bpm"),
            "bone_density_loss": ("Bone Density Loss", "%/mo"),
            "radiation_dose": ("Radiation Dose", "mSv/day"),
            "sleep_hours": ("Sleep", "hrs"),
        }
        for i, (key, (label, unit)) in enumerate(labels.items()):
            value = latest[key]
            status = main.evaluate_status(key, value)
            with metric_cols[i]:
                st.metric(label, f"{value:.1f} {unit}")
                st.write(f"{STATUS_COLOR[status]} {status.capitalize()}")
    else:
        st.info("Create a profile, then click 'Take reading' to start.")
 
st.divider()
 
if not st.session_state.history.empty:
    st.subheader("Trends")
    chart_cols = st.columns(2)
    metrics = ["heart_rate", "bone_density_loss", "radiation_dose", "sleep_hours"]
    for i, m in enumerate(metrics):
        with chart_cols[i % 2]:
            st.line_chart(st.session_state.history.set_index("time")[[m]])