import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import storage.storage as s


def test_load_users_missing(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"
    monkeypatch.setattr(s, "USERS_FILE", test_file)
    assert s.load_users() == {}


def test_init_and_update_user(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"
    monkeypatch.setattr(s, "USERS_FILE", test_file)

    s.init_user(123, "0xabc")
    user = s.get_user(123)
    assert user["address"] == "0xabc"
    assert user["lp_fees_threshold"] == 20
    assert user["hf_thresholds"] == [1.5, 1.3]
    assert user["price_alerts"]["eth"] == 10

    s.update_user(123, "lp_fees_threshold", 25)
    updated = s.get_user(123)
    assert updated["lp_fees_threshold"] == 25

    s.update_user(123, "address", "привет")

    with open(test_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data[str(123)]["lp_fees_threshold"] == 25
    assert "привет" in open(test_file, encoding="utf-8").read()


def test_load_users_corrupt(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"
    test_file.write_text("{invalid json", encoding="utf-8")
    monkeypatch.setattr(s, "USERS_FILE", test_file)
    assert s.load_users() == {}


def test_get_user_creates_new(tmp_path, monkeypatch):
    test_file = tmp_path / "users.json"
    monkeypatch.setattr(s, "USERS_FILE", test_file)

    user = s.get_user(555)
    assert user["address"] == ""
    assert user["hf_thresholds"] == [1.5, 1.3]
    with open(test_file, encoding="utf-8") as f:
        data = json.load(f)
    assert str(555) in data
