import random
from database import update_balance, add_transaction

MULTIPLIERS = [0, 0.5, 1, 1.5, 2, 3, 5]  # 0 = проигрыш

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("🎡 !колесо <ставка>")
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
    mult = random.choice(MULTIPLIERS)
    if mult == 0:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        await update.message.reply_text(f"🎡 Колесо остановилось на 0x. Вы потеряли {bet}💰.")
    else:
        profit = int(bet * mult)
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        await update.message.reply_text(f"🎡 Колесо показало {mult}x! Вы выиграли {profit}💰.")
