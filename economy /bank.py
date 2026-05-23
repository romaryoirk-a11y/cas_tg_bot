from datetime import datetime, timezone
from database import get_user, add_transaction

INTEREST_RATE = 0.05   # 5% в день
BANK_COOLDOWN = 24 * 3600

async def apply_bank_interest(pool, user):
    now = datetime.now(timezone.utc)
    last = user["last_bank_interest"]
    if (now - last).total_seconds() >= BANK_COOLDOWN and user["bank_balance"] > 0:
        interest = int(user["bank_balance"] * INTEREST_RATE)
        await pool.execute(
            "UPDATE users SET bank_balance = bank_balance + $1, last_bank_interest = $2 WHERE user_id=$3",
            interest, now, user["user_id"]
        )
        await add_transaction(pool, user["user_id"], "bank_interest", interest)
        user["bank_balance"] += interest
        user["last_bank_interest"] = now
    elif (now - last).total_seconds() >= BANK_COOLDOWN:
        await pool.execute(
            "UPDATE users SET last_bank_interest = $1 WHERE user_id=$2",
            now, user["user_id"]
        )
        user["last_bank_interest"] = now
    return user

async def handler(update, context):
    user_id = update.effective_user.id
    pool = context.bot_data["pool"]
    user = await get_user(pool, user_id)
    user = await apply_bank_interest(pool, user)

    args = context.args
    if not args:
        await update.message.reply_text(
            f"🏦 Банк\n"
            f"Баланс: {user['balance']}💰\n"
            f"В банке: {user['bank_balance']}💰 (доход {INTEREST_RATE*100}% в день)\n"
            f"Команды: /банк вклад <сумма>, /банк снять <сумма>"
        )
        return

    sub = args[0].lower()
    if sub == "вклад":
        if len(args) < 2:
            await update.message.reply_text("Укажите сумму: /банк вклад 1000")
            return
        amount = int(args[1])
        if amount <= 0 or amount > user["balance"]:
            await update.message.reply_text("❌ Недостаточно средств или неверная сумма.")
            return
        await pool.execute(
            "UPDATE users SET balance = balance - $1, bank_balance = bank_balance + $1 WHERE user_id=$2",
            amount, user_id
        )
        await add_transaction(pool, user_id, "bank_deposit", -amount)
        await update.message.reply_text(f"💰 {amount} положено в банк.")
    elif sub == "снять":
        if len(args) < 2:
            await update.message.reply_text("Укажите сумму: /банк снять 500")
            return
        amount = int(args[1])
        if amount <= 0 or amount > user["bank_balance"]:
            await update.message.reply_text("❌ Недостаточно средств в банке или неверная сумма.")
            return
        await pool.execute(
            "UPDATE users SET balance = balance + $1, bank_balance = bank_balance - $1 WHERE user_id=$2",
            amount, user_id
        )
        await add_transaction(pool, user_id, "bank_withdraw", amount)
        await update.message.reply_text(f"💰 {amount} снято с банковского счёта.")
    else:
        await update.message.reply_text("Неизвестная команда. Используйте вклад или снять.")
