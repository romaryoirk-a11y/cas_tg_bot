import random
from datetime import datetime, timezone
from database import get_user, update_balance, add_transaction

BONUS_COOLDOWN = 4 * 3600  # 4 часа

async def handler(update, context):
    user_id = update.effective_user.id
    pool = context.bot_data["pool"]
    user = await get_user(pool, user_id)
    now = datetime.now(timezone.utc)
    last = user["last_bonus"]
    if last and (now - last).total_seconds() < BONUS_COOLDOWN:
        remaining = BONUS_COOLDOWN - (now - last).total_seconds()
        h = int(remaining // 3600)
        m = int((remaining % 3600) // 60)
        await update.message.reply_text(f"Бонус доступен через {h}ч {m}мин.")
        return
    amount = random.randint(1000, 6000)
    await pool.execute("UPDATE users SET balance = balance + $1, last_bonus = $2 WHERE user_id=$3",
                       amount, now, user_id)
    await add_transaction(pool, user_id, "bonus", amount)
    await update.message.reply_text(f"🎁 Вы получили ежедневный бонус: {amount}💰!")
