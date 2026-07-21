import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "kuesioner.json")


def load_kuesioner() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_profile(profiles: list, total_score: int) -> dict:
    for p in profiles:
        if p["min_score"] <= total_score <= p["max_score"]:
            return p
    return profiles[-1] if profiles else None
