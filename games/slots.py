import random
from database import update_balance, add_transaction

SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("🎰 !сл <ставка>")
        return
    try:
        bet = int(args[0])
    except ValueError:
        await update.message.reply_text("Ставка — число.")
        return
    pool = context.bot_data["pool"]
    user = await pool.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
    if user["balance"] < bet or bet <= 0:
        await update.message.reply_text("Недостаточно средств.")
        return
    result = [random.choice(SYMBOLS) for _ in range(3)]
    if result[0] == result[1] == result[2]:
        profit = bet * 10
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        text = f"{' '.join(result)} — Джекпот! Вы выиграли {profit}💰"
    elif result[0] == result[1] or result[1] == result[2]:
        profit = bet * 2
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        text = f"{' '.join(result)} — Два совпадения. Выигрыш: {profit}💰"
    else:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        text = f"{' '.join(result)} — Вы проиграли {bet}💰."
    await update.message.reply_text(text)
