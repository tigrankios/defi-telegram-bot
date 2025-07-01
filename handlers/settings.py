"""Handlers for managing user settings commands."""

from aiogram import Dispatcher, types
from aiogram.filters import Command

FORMAT_ERROR = "⚠️ Неверный формат. Используйте: {}"

from storage.storage import get_user, update_user


async def set_hf_threshold(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(FORMAT_ERROR.format("/set_hf_threshold 1.5"))
        return
    try:
        value = float(parts[1])
    except ValueError:
        await message.answer(FORMAT_ERROR.format("/set_hf_threshold 1.5"))
        return
    user = get_user(message.chat.id)
    thresholds = user.get("hf_thresholds", [1.5, 1.3])
    if len(thresholds) < 2:
        thresholds = [value, 1.3]
    else:
        thresholds[0] = value
    update_user(message.chat.id, "hf_thresholds", thresholds)
    await message.answer(f"✅ Порог HF обновлён до {value}")


async def set_sr_threshold(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(FORMAT_ERROR.format("/set_sr_threshold 150"))
        return
    try:
        value = float(parts[1])
    except ValueError:
        await message.answer(FORMAT_ERROR.format("/set_sr_threshold 150"))
        return
    user = get_user(message.chat.id)
    thresholds = user.get("sr_thresholds", [150, 130])
    if len(thresholds) < 2:
        thresholds = [value, 130]
    else:
        thresholds[0] = value
    update_user(message.chat.id, "sr_thresholds", thresholds)
    await message.answer(f"✅ Порог SR обновлён до {value}")


async def set_fees_threshold(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(FORMAT_ERROR.format("/set_fees_threshold 20"))
        return
    try:
        value = float(parts[1])
    except ValueError:
        await message.answer(FORMAT_ERROR.format("/set_fees_threshold 20"))
        return
    update_user(message.chat.id, "lp_fees_threshold", value)
    await message.answer(f"✅ Порог LP-комиссий обновлён до {value}")


async def set_price_threshold(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer(FORMAT_ERROR.format("/set_price_threshold eth 10"))
        return
    asset = parts[1].lower()
    try:
        percent = float(parts[2])
    except ValueError:
        await message.answer(FORMAT_ERROR.format("/set_price_threshold eth 10"))
        return
    if asset not in {"eth", "btc"}:
        await message.answer(FORMAT_ERROR.format("/set_price_threshold eth 10"))
        return
    user = get_user(message.chat.id)
    alerts = user.get("price_alerts", {})
    alerts[asset] = percent
    update_user(message.chat.id, "price_alerts", alerts)
    await message.answer(f"✅ Порог изменения цены {asset.upper()} обновлён до {percent}%")


async def show_alerts(message: types.Message) -> None:
    user = get_user(message.chat.id)
    alerts = user.get("alerts", {})
    lines = [f"{k}: {'on' if v else 'off'}" for k, v in alerts.items()]
    text = "\n".join(lines) if lines else "Нет данных"
    await message.answer(text)


async def toggle_alert(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer(FORMAT_ERROR.format("/alerts hf off"))
        return
    alert_type = parts[1].lower()
    state = parts[2].lower()
    if alert_type not in {"hf", "sr", "lp_range", "lp_fees", "prices"} or state not in {"on", "off"}:
        await message.answer(FORMAT_ERROR.format("/alerts hf off"))
        return
    user = get_user(message.chat.id)
    alerts = user.get("alerts", {})
    alerts[alert_type] = state == "on"
    update_user(message.chat.id, "alerts", alerts)
    await message.answer("✅ Настройки уведомлений обновлены")


def register(dp: Dispatcher) -> None:
    dp.message.register(set_hf_threshold, Command("set_hf_threshold"))
    dp.message.register(set_sr_threshold, Command("set_sr_threshold"))
    dp.message.register(set_fees_threshold, Command("set_fees_threshold"))
    dp.message.register(set_price_threshold, Command("set_price_threshold"))
    dp.message.register(show_alerts, Command("alerts"), lambda msg: len(msg.text.split()) == 1)
    dp.message.register(toggle_alert, Command("alerts"), lambda msg: len(msg.text.split()) == 3)
