import sys
from pathlib import Path
import types
import asyncio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

aiogram_stub = types.SimpleNamespace(
    Dispatcher=object,
    types=types.SimpleNamespace(Message=object),
)
sys.modules.setdefault("aiogram", aiogram_stub)
sys.modules.setdefault("aiogram.filters", types.SimpleNamespace(Command=object))

import handlers.lp as lp
import storage.storage as s


class DummyMessage:
    def __init__(self, text, chat_id=1):
        self.text = text
        self.chat = types.SimpleNamespace(id=chat_id)
        self.responses = []

    async def answer(self, text):
        self.responses.append(text)


def test_add_lp(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(1, "0x")

    msg = DummyMessage("/add_lp eth/usdc", 1)
    asyncio.run(lp.add_lp(msg))

    assert msg.responses[-1] == "✅ Пара ETH/USDC добавлена"
    user = s.get_user(1)
    assert user["lp_pairs"] == ["ETH/USDC"]


def test_add_lp_duplicate(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(2, "0x")

    msg1 = DummyMessage("/add_lp ETH/USDC", 2)
    asyncio.run(lp.add_lp(msg1))

    msg2 = DummyMessage("/add_lp eth/usdc", 2)
    asyncio.run(lp.add_lp(msg2))

    assert msg2.responses[-1] == "⚠️ Пара ETH/USDC уже добавлена"
    user = s.get_user(2)
    assert user["lp_pairs"] == ["ETH/USDC"]


def test_remove_lp(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(3, "0x")
    s.update_user(3, "lp_pairs", ["ETH/USDC"])

    msg = DummyMessage("/remove_lp eth/usdc", 3)
    asyncio.run(lp.remove_lp(msg))

    assert msg.responses[-1] == "✅ Пара ETH/USDC удалена"
    user = s.get_user(3)
    assert user["lp_pairs"] == []


def test_remove_lp_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(4, "0x")

    msg = DummyMessage("/remove_lp eth/usdc", 4)
    asyncio.run(lp.remove_lp(msg))

    assert msg.responses[-1] == "⚠️ Пара ETH/USDC не найдена"


def test_lp_list(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(5, "0x")

    empty_msg = DummyMessage("/lp_list", 5)
    asyncio.run(lp.lp_list(empty_msg))
    assert empty_msg.responses[-1] == "ℹ️ Нет добавленных LP-пар"

    s.update_user(5, "lp_pairs", ["ETH/USDC", "WBTC/ETH"])
    filled_msg = DummyMessage("/lp_list", 5)
    asyncio.run(lp.lp_list(filled_msg))

    resp = filled_msg.responses[-1]
    assert "ETH/USDC" in resp and "WBTC/ETH" in resp


def test_status_output(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "USERS_FILE", tmp_path / "users.json")
    s.init_user(6, "0xabc")

    msg = DummyMessage("/status", 6)
    asyncio.run(lp.status(msg))

    resp = msg.responses[-1]
    assert "👤 Адрес: 0xabc" in resp
    assert "HF: 1.5 / 1.3" in resp
    assert "SR: 150 / 130" in resp
    assert "LP Fee Threshold: $20" in resp
