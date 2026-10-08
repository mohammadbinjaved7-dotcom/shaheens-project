import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DATA_FILE = "astronauts.json"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

THRESHOLDS = {
    "heart_rate": (60, 100),
    "bone_density_loss": (0, 1.5),
    "radiation_dose": (0, 0.8),
    "sleep_hours": (6, 9),
}

METRIC_LABELS = {
    "heart_rate": ("Heart rate", "bpm"),
    "bone_density_loss": ("Bone density loss", "%/month"),
    "radiation_dose": ("Radiation dose", "mSv/day"),
    "sleep_hours": ("Sleep", "hours"),
}


def evaluate_status(metric_name, value):
    lo, hi = THRESHOLDS[metric_name]
    if lo <= value <= hi:
        return "normal"
    margin = (hi - lo) * 0.3
    if value < lo - margin or value > hi + margin:
        return "critical"
    return "warning"


def new_profile(name, age, sex, weight_kg, height_cm, activity_level):
    return {
        "name": name,
        "age": age,
        "sex": sex,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "activity_level": activity_level,
        "readings": [],
    }




def load_all_profiles(path=DATA_FILE):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_all_profiles(all_profiles, path=DATA_FILE):
    with open(path, "w") as f:
        json.dump(all_profiles, f, indent=2)


def get_profile(username, path=DATA_FILE):
    return load_all_profiles(path).get(username)


def save_profile(username, profile, path=DATA_FILE):
    all_profiles = load_all_profiles(path)
    all_profiles[username] = profile
    save_all_profiles(all_profiles, path)


def add_reading(username, reading, path=DATA_FILE):
    all_profiles = load_all_profiles(path)
    if username not in all_profiles:
        return None
    all_profiles[username]["readings"].append(reading)
    save_all_profiles(all_profiles, path)
    return all_profiles[username]



ACTIVITY_MULTIPLIERS = {
    "low": 1.2,
    "moderate": 1.55,
    "high": 1.725,
}


def calculate_calories(profile):
    w = profile["weight_kg"]
    h = profile["height_cm"]
    age = profile["age"]

    if profile["sex"] == "M":
        bmr = 10 * w + 6.25 * h - 5 * age + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * age - 161

    multiplier = ACTIVITY_MULTIPLIERS.get(profile.get("activity_level", "moderate"), 1.55)
    return round(bmr * multiplier)



def _format_normal_ranges():
    lines = []
    for key, (label, unit) in METRIC_LABELS.items():
        lo, hi = THRESHOLDS[key]
        lines.append(f"- {label}: {lo}-{hi} {unit}")
    return "\n".join(lines)


def get_health_advice(question, profile, history):
    latest = history.iloc[-1].to_dict() if not history.empty else {}

    context = f"""
    Astronaut: {profile['name']}, age {profile['age']}, {profile['activity_level']} activity level.
    Latest reading: {latest}

    Normal ranges:
    {_format_normal_ranges()}
    """

    prompt = context + f"\n\nQuestion: {question}\n\nAnswer briefly and practically."

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def main():
    pass


if __name__ == "__main__":
    main()