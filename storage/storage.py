import json
from pathlib import Path
from typing import Any, Dict
import logging

USERS_FILE = Path(__file__).resolve().parent / "users.json"


def load_users() -> Dict[str, Any]:
    """Загружает все данные пользователей из users.json."""
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logging.error("Failed to load users from %s: %s", USERS_FILE, e)
    return {}


def save_users(users: Dict[str, Any]) -> None:
    """Сохраняет все данные обратно в файл."""
    try:
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logging.error("Failed to save users to %s: %s", USERS_FILE, e)


def get_user(chat_id: int) -> Dict[str, Any]:
    """Возвращает словарь с настройками конкретного пользователя."""
    users = load_users()
    chat_id_str = str(chat_id)
    if chat_id_str not in users:
        init_user(chat_id, "")
        return load_users().get(chat_id_str, {})
    return users[chat_id_str]


def update_user(chat_id: int, key: str, value: Any) -> None:
    """Обновляет поле пользователя и сохраняет."""
    users = load_users()
    user = users.get(str(chat_id), {})
    user[key] = value
    users[str(chat_id)] = user
    save_users(users)


def init_user(chat_id: int, address: str) -> None:
    """Создаёт новый профиль пользователя с базовыми значениями."""
    users = load_users()
    if str(chat_id) not in users:
        users[str(chat_id)] = {
            "address": address,
            "hf_thresholds": [1.5, 1.3],
            "sr_thresholds": [150, 130],
            "lp_pairs": [],
            "lp_fees_threshold": 20,
            "price_alerts": {
                "eth": 10,
                "btc": 5,
            },
            "alerts": {
                "hf": True,
                "sr": True,
                "lp_range": True,
                "lp_fees": True,
                "prices": True,
            },
        }
        save_users(users)
