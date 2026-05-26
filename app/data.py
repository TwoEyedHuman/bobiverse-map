import json
import math
import os

import pandas as pd

SYSTEM_COORDS = {
    "Sol": (0, 0),
    "Alpha Centauri": (4.37, 0.2),
    "Epsilon Eridani": (10.5, -2.1),
    "Omicron Eridani": (16.2, -5.8),
    "Delta Eridani": (29.5, 4.2),
    "82 Eridani": (19.7, -5.0),
    "Beta Hydri": (24.3, -14.5),
    "Sigma Draconis": (18.8, 12.1),
    "Tau Ceti": (11.9, -1.5),
    "Epsilon Indi": (11.8, -2.5),
}


def get_coords(system_name):
    return SYSTEM_COORDS.get(system_name, (0, 0))


def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "bobs.json")
    with open(data_path) as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    df["assumed_date"] = pd.to_datetime(df["assumed_date"])
    df = df.sort_values(["bob", "assumed_date"])
    return df


def compute_positions(df, selected_date):
    bobs = df["bob"].unique()
    processed_positions = []

    for bob in bobs:
        bob_data = df[df["bob"] == bob].sort_values("assumed_date")
        past_data = bob_data[bob_data["assumed_date"] <= selected_date]
        future_data = bob_data[bob_data["assumed_date"] > selected_date]

        if past_data.empty:
            continue

        last_entry = past_data.iloc[-1]
        prev_coords = get_coords(last_entry["system"])
        angle = 0
        is_traveling = False
        travel_path = None

        if not future_data.empty:
            next_entry = future_data.iloc[0]
            next_coords = get_coords(next_entry["system"])

            if next_entry["system"] != last_entry["system"]:
                is_traveling = True
                time_diff = (
                    next_entry["assumed_date"] - last_entry["assumed_date"]
                ).total_seconds()
                elapsed = (selected_date - last_entry["assumed_date"]).total_seconds()
                fraction = elapsed / time_diff if time_diff > 0 else 0

                curr_x = prev_coords[0] + (next_coords[0] - prev_coords[0]) * fraction
                curr_y = prev_coords[1] + (next_coords[1] - prev_coords[1]) * fraction

                dx = next_coords[0] - prev_coords[0]
                dy = next_coords[1] - prev_coords[1]
                angle = 90 - (math.atan2(dy, dx) * 180 / math.pi)

                travel_path = (
                    [prev_coords[0], next_coords[0]],
                    [prev_coords[1], next_coords[1]],
                )
                status = f"Traveling to {next_entry['system']}"
            else:
                curr_x, curr_y = prev_coords
                status = f"Stationary at {last_entry['system']}"
        else:
            curr_x, curr_y = prev_coords
            status = f"Stationary at {last_entry['system']}"

        processed_positions.append(
            {
                "name": bob,
                "x": curr_x,
                "y": curr_y,
                "angle": angle,
                "status": status,
                "is_traveling": is_traveling,
                "last_date": last_entry["assumed_date"].date(),
                "path": travel_path,
            }
        )

    return processed_positions
