import sys
from pathlib import Path
import asyncio
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# provide minimal aiogram stub
aiogram_stub = types.ModuleType("aiogram")
aiogram_stub.Bot = object
aiogram_stub.Dispatcher = object
aiogram_stub.types = types.SimpleNamespace(Message=object)
sys.modules['aiogram'] = aiogram_stub
sys.modules['aiogram.filters'] = types.SimpleNamespace(Command=object)

# dummy Bot used by Monitor
class DummyBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))

import storage.storage as s
from services.monitor import Monitor


def setup_user(tmp_path, alerts=None):
    s.USERS_FILE = tmp_path / 'users.json'
    s.init_user(1, '0xabc')
    if alerts is not None:
        s.update_user(1, 'alerts', alerts)
    return s.get_user(1)


def test_check_user_sends_expected_alerts(tmp_path, monkeypatch):
    monkeypatch.setattr('services.monitor.time.monotonic', lambda: 1000)
    user = setup_user(tmp_path)
    bot = DummyBot()
    mon = Monitor(bot)
    asyncio.run(mon.check_user(1, user))
    texts = [t for _, t in bot.sent]
    assert 'Health Factor' in texts[0]
    assert 'Safety Ratio' in texts[1]
    assert 'вышла из диапазона' in texts[2]
    assert 'превысил $20' in texts[3]


def test_price_alert_and_state_update(tmp_path, monkeypatch):
    monkeypatch.setattr('services.monitor.time.monotonic', lambda: 1000)
    setup_user(tmp_path, alerts={'prices': True})
    s.update_user(1, 'price_alerts', {'eth': 5})
    s.update_user(1, 'eth_price', 2000)
    bot = DummyBot()
    mon = Monitor(bot)
    asyncio.run(mon.check_user(1, s.get_user(1)))
    assert any(text.startswith('📉 ETH изменился') for _, text in bot.sent)
    assert s.get_user(1)['eth_price'] == 1800


def test_send_alert_throttle(monkeypatch):
    bot = DummyBot()
    mon = Monitor(bot)
    monkeypatch.setattr('services.monitor.time.monotonic', lambda: 1000)
    asyncio.run(mon._send_alert(1, 'hf', 'first'))
    asyncio.run(mon._send_alert(1, 'hf', 'second'))
    assert bot.sent == [(1, 'first')]
