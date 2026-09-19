import json

DATA_FILE = "astronaut_data.json"

import numpy as np

def get_latest_reading():
    return {
        "heart_rate": np.random.normal(75, 8),
        "bone_density_loss": np.random.normal(1.0, 0.3),
        "radiation_dose": np.random.normal(0.3, 0.1),
        "sleep_hours": np.random.normal(6.5, 1.0),
    }


def load_profile(path=DATA_FILE):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None




def evaluate_status(metric_name, value):
    pass


def new_profile(name, age, sex, weight_kg, height_cm, activity_level):
    pass


def save_profile(profile, path=DATA_FILE):
    pass


def calculate_calories(profile):
    pass


def main():
    pass

if __name__ == "__main__":
    main()