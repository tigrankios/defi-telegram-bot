import asyncio
import logging
import time
from typing import Dict, Tuple

from aiogram import Bot

from storage.storage import load_users, update_user

from .aave import AaveService
from .revert import RevertService
from .coingecko import CoingeckoService


class Monitor:
    """Periodically check user positions and send alerts."""

    def __init__(self, bot: Bot, interval: int = 60):
        self.bot = bot
        self.interval = interval
        self.aave = AaveService()
        self.revert = RevertService()
        self.coingecko = CoingeckoService()
        self._last_alerts: Dict[Tuple[int, str], float] = {}

    async def _send_alert(self, chat_id: int, category: str, text: str) -> None:
        now = time.monotonic()
        key = (chat_id, category)
        if now - self._last_alerts.get(key, 0) < 300:
            return
        try:
            await self.bot.send_message(chat_id, text)
            self._last_alerts[key] = now
        except Exception as e:  # pragma: no cover - network related
            logging.error("Failed to send alert: %s", e)

    async def check_user(self, chat_id: int, user: dict) -> None:
        address = user.get("address")
        if not address:
            return
        alerts = user.get("alerts", {})
        if alerts.get("hf"):
            hf = await self.aave.get_health_factor(address)
            for threshold in user.get("hf_thresholds", []):
                if hf < threshold:
                    await self._send_alert(
                        chat_id,
                        "hf",
                        f"⚠️ Health Factor упал ниже {threshold}! (Текущее значение: {hf})",
                    )
                    break
        if alerts.get("sr"):
            sr = await self.aave.get_safety_ratio(address)
            for threshold in user.get("sr_thresholds", []):
                if sr < threshold:
                    await self._send_alert(
                        chat_id,
                        "sr",
                        f"⚠️ Safety Ratio упал ниже {threshold}! (Текущее значение: {sr})",
                    )
                    break
        positions = []
        if alerts.get("lp_range") or alerts.get("lp_fees"):
            positions = await self.revert.get_active_lps(address)
        if alerts.get("lp_range"):
            for p in positions:
                if not p.get("in_range", True):
                    await self._send_alert(
                        chat_id,
                        f"lp_range_{p['pair']}",
                        f"⚠️ Пара {p['pair']} вышла из диапазона!",
                    )
        if alerts.get("lp_fees"):
            threshold = user.get("lp_fees_threshold", 0)
            for p in positions:
                if p.get("fees_usd", 0) > threshold:
                    await self._send_alert(
                        chat_id,
                        f"lp_fees_{p['pair']}",
                        f"💰 Доход по паре {p['pair']} превысил ${threshold}!",
                    )
        if alerts.get("prices"):
            price_alerts = user.get("price_alerts", {})
            for asset, percent in price_alerts.items():
                price = await self.coingecko.get_price(asset)
                last_key = f"{asset}_price"
                prev = user.get(last_key)
                if prev is not None:
                    change = abs(price - prev) / prev * 100 if prev else 0
                    if change > percent:
                        arrow = "📉" if price < prev else "📈"
                        await self._send_alert(
                            chat_id,
                            f"price_{asset}",
                            f"{arrow} {asset.upper()} изменился на {round(change, 2)}%",
                        )
                update_user(chat_id, last_key, price)

    async def run(self) -> None:
        while True:
            users = load_users()
            for chat_id_str, user in users.items():
                try:
                    await self.check_user(int(chat_id_str), user)
                except Exception as e:  # pragma: no cover - runtime logging
                    logging.error("Monitor error for %s: %s", chat_id_str, e)
            await asyncio.sleep(self.interval)


async def monitor_all_users(bot: Bot, interval: int = 60) -> None:
    monitor = Monitor(bot, interval)
    await monitor.run()
