import sys
from pathlib import Path
import types
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

aiogram_stub = types.SimpleNamespace(
    Dispatcher=object,
    types=types.SimpleNamespace(Message=object),
)
sys.modules.setdefault("aiogram", aiogram_stub)
sys.modules.setdefault("aiogram.filters", types.SimpleNamespace(Command=object))

import handlers.settings as h
import storage.storage as s


class DummyMessage:
    def __init__(self, text, chat_id=1):
        self.text = text
        self.chat = types.SimpleNamespace(id=chat_id)
        self.responses = []

    async def answer(self, text):
        self.responses.append(text)


def test_set_hf_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(1, "0x")

    msg = DummyMessage("/set_hf_threshold 2.0", 1)
    import asyncio
    asyncio.run(h.set_hf_threshold(msg))

    assert msg.responses[-1] == "✅ Порог HF обновлён до 2.0"
    data = s.load_users()
    assert data["1"]["hf_thresholds"][0] == 2.0


def test_toggle_alert_respects_case(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(5, "0x")

    msg = DummyMessage("/alerts HF off", 5)
    import asyncio
    asyncio.run(h.toggle_alert(msg))

    user = s.get_user(5)
    assert user["alerts"]["hf"] is False

