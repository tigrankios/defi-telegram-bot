"""LP pair management and user status commands."""

from aiogram import Dispatcher, types
from aiogram.filters import Command

from storage.storage import get_user, update_user

FORMAT_ERROR = "⚠️ Неверный формат. Используйте: {}"


async def add_lp(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(FORMAT_ERROR.format("/add_lp ETH/USDC"))
        return
    pair = parts[1].upper()
    user = get_user(message.chat.id)
    pairs = user.get("lp_pairs", [])
    if pair in pairs:
        await message.answer(f"⚠️ Пара {pair} уже добавлена")
        return
    pairs.append(pair)
    update_user(message.chat.id, "lp_pairs", pairs)
    await message.answer(f"✅ Пара {pair} добавлена")


async def remove_lp(message: types.Message) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(FORMAT_ERROR.format("/remove_lp ETH/USDC"))
        return
    pair = parts[1].upper()
    user = get_user(message.chat.id)
    pairs = user.get("lp_pairs", [])
    if pair not in pairs:
        await message.answer(f"⚠️ Пара {pair} не найдена")
        return
    pairs.remove(pair)
    update_user(message.chat.id, "lp_pairs", pairs)
    await message.answer(f"✅ Пара {pair} удалена")


async def lp_list(message: types.Message) -> None:
    user = get_user(message.chat.id)
    pairs = user.get("lp_pairs", [])
    if not pairs:
        await message.answer("ℹ️ Нет добавленных LP-пар")
        return
    lines = "\n\t•\t".join(pairs)
    await message.answer(f"🔍 Отслеживаемые пары:\n\t•\t{lines}")


async def status(message: types.Message) -> None:
    """Show current user settings in a formatted message."""

    user = get_user(message.chat.id)

    address = user.get("address", "")

    hf = user.get("hf_thresholds", [])
    hf_text = " / ".join(str(x) for x in hf) if hf else "—"

    sr = user.get("sr_thresholds", [])
    sr_text = " / ".join(str(x) for x in sr) if sr else "—"

    lp_fees = user.get("lp_fees_threshold")
    fees_text = f"${lp_fees}" if lp_fees is not None else "—"

    price_alerts = user.get("price_alerts", {})
    if price_alerts:
        price_lines = "\n\t•\t" + "\n\t•\t".join(
            f"{k.upper()}: {v}%" for k, v in price_alerts.items()
        )
    else:
        price_lines = " —"

    lp_pairs = user.get("lp_pairs", [])
    if lp_pairs:
        lp_lines = "\n\t•\t" + "\n\t•\t".join(lp_pairs)
    else:
        lp_lines = " —"

    alerts = user.get("alerts", {})
    if alerts:
        alerts_text = "\n".join(
            f"{k}: {'on' if v else 'off'}" for k, v in alerts.items()
        )
    else:
        alerts_text = "—"

    text = (
        f"👤 Адрес: {address or '—'}\n"
        f"📉 HF: {hf_text}\n"
        f"📈 SR: {sr_text}\n"
        f"💰 LP Fee Threshold: {fees_text}\n"
        f"📊 Price Alerts:{price_lines}\n"
        f"💼 LP-пары:{lp_lines}\n"
        f"🔔 Алерты:\n{alerts_text}"
    )
    await message.answer(text)


def register(dp: Dispatcher) -> None:
    dp.message.register(add_lp, Command("add_lp"))
    dp.message.register(remove_lp, Command("remove_lp"))
    dp.message.register(lp_list, Command("lp_list"))
    dp.message.register(status, Command("status"))
