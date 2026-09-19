import json
import numpy

DATA_FILE = ""

import numpy as np

def get_latest_reading():
    return {
        "heart_rate": np.random.normal(75, 8),
        "bone_density_loss": np.random.normal(1.0, 0.3),
        "radiation_dose": np.random.normal(0.3, 0.1),
        "sleep_hours": np.random.normal(6.5, 1.0),
    }

def main():
    pass

def load_profile(path=DATA_FILE):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None




if __name__ == "__main__":
    main()