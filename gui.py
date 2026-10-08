import streamlit as st
import pandas as pd

import main

st.set_page_config(page_title="Astronaut Health Monitor", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://media.discordapp.net/attachments/964456556429193238/1552721422843908106/image.png?ex=6ab6a403&is=6ab55283&hm=94e12a9e994f509206753a883ee86d2df83dd403bb07e3b16d16729bf3fc9891&=&format=webp&quality=lossless&width=1280&height=960');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

STATUS_COLOR = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}


def build_history_df(profile):
    readings = profile.get("readings", [])
    df = pd.DataFrame(readings)
    if df.empty:
        df = pd.DataFrame(columns=["time", "heart_rate", "bone_density_loss", "radiation_dose", "sleep_hours"])
    else:
        df.insert(0, "time", range(len(df)))
    return df


if "username" not in st.session_state:
    st.session_state.username = None
if "profile" not in st.session_state:
    st.session_state.profile = None
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["time", "heart_rate", "bone_density_loss", "radiation_dose", "sleep_hours"]
    )
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if st.session_state.username is None:
    st.title(" Astronaut Health Monitor")
    st.caption("Enter a username to log in. New usernames start a fresh profile.")

    with st.form("login_form"):
        username_input = st.text_input("Username")
        login_submitted = st.form_submit_button("Continue")
        if login_submitted and username_input.strip():
            username = username_input.strip()
            st.session_state.username = username
            existing_profile = main.get_profile(username)
            if existing_profile:
                st.session_state.profile = existing_profile
                st.session_state.history = build_history_df(existing_profile)
            st.rerun()

    st.stop()


st.title(" Astronaut Health Monitor")
st.caption("Live health indicators. Flags issues before they become emergencies.")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader(f"Logged in as {st.session_state.username}")
    if st.button("Log out"):
        st.session_state.username = None
        st.session_state.profile = None
        st.session_state.history = pd.DataFrame(
            columns=["time", "heart_rate", "bone_density_loss", "radiation_dose", "sleep_hours"]
        )
        st.session_state.chat_history = []
        st.rerun()

    st.divider()
    st.subheader("Astronaut Profile")

    if st.session_state.profile is None:
        st.write("No profile found for this username yet. Please, create one below.")
        with st.form("profile_form"):
            name = st.text_input("Name", st.session_state.username)
            age = st.number_input("Age", 18, 70, 40)
            sex = st.selectbox("Sex", ["M", "F"])
            weight = st.number_input("Weight (kg)", 40, 150, 78)
            height = st.number_input("Height (cm)", 140, 220, 180)
            activity = st.selectbox("Activity level", ["low", "moderate", "high"])
            submitted = st.form_submit_button("Create profile")
            if submitted:
                profile = main.new_profile(name, age, sex, weight, height, activity)
                main.save_profile(st.session_state.username, profile)
                st.session_state.profile = profile
                st.rerun()
    else:
        p = st.session_state.profile
        st.write(f"**{p['name']}**")
        st.write(f"{p['age']}y, {p['weight_kg']}kg, {p['height_cm']}cm")
        calories = main.calculate_calories(p)
        st.metric("Recommended daily intake", f"{calories} kcal")

        st.write("**Enter today's reading**")
        with st.form("reading_form"):
            heart_rate = st.number_input("Heart rate (bpm)", 30, 220, 75)
            bone_density_loss = st.number_input("Bone density loss (%/mo)", 0.0, 5.0, 1.0)
            radiation_dose = st.number_input("Radiation dose (mSv/day)", 0.0, 5.0, 0.5)
            sleep_hours = st.number_input("Sleep (hrs)", 0.0, 14.0, 6.5)
            reading_submitted = st.form_submit_button("Submit reading")
            if reading_submitted:
                reading = {
                    "heart_rate": heart_rate,
                    "bone_density_loss": bone_density_loss,
                    "radiation_dose": radiation_dose,
                    "sleep_hours": sleep_hours,
                }
                main.add_reading(st.session_state.username, reading)
                st.session_state.profile["readings"].append(reading)
                st.session_state.history = build_history_df(st.session_state.profile)
                st.rerun()

with col2:
    if st.session_state.profile is None:
        st.info("Create a profile to get started.")
    elif st.session_state.history.empty:
        st.info("Submit a reading to see your health metrics.")
    else:
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

st.divider()

if not st.session_state.history.empty:
    st.subheader("Trends")
    chart_cols = st.columns(2)
    metrics = ["heart_rate", "bone_density_loss", "radiation_dose", "sleep_hours"]
    for i, m in enumerate(metrics):
        with chart_cols[i % 2]:
            st.line_chart(st.session_state.history.set_index("time")[[m]])

st.subheader("Ask the health assistant")

if st.session_state.profile is not None:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask something about your health data...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        answer = main.get_health_advice(question, st.session_state.profile, st.session_state.history)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)
else:
    st.info("Create a profile first to use the assistant.")