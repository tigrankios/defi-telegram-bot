import json
from pathlib import Path

STORAGE_PATH = Path(__file__).resolve().parent / "storage" / "users.json"


def load_users() -> dict:
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH) as f:
            return json.load(f)
    return {}


def save_users(data: dict) -> None:
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)
