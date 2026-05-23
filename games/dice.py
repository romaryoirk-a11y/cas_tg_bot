import random
from database import update_balance, add_transaction

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("🎲 !к <ставка> <число 1-6>")
        return
    try:
        bet = int(args[0])
        guess = int(args[1])
    except ValueError:
        await update.message.reply_text("Неверный формат.")
        return
    if not 1 <= guess <= 6:
        await update.message.reply_text("Число от 1 до 6.")
        return
    pool = context.bot_data["pool"]
    user = await pool.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
    if user["balance"] < bet or bet <= 0:
        await update.message.reply_text("Недостаточно средств.")
        return
    dice = random.randint(1, 6)
    if dice == guess:
        profit = bet * 6
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        await update.message.reply_text(f"🎲 Выпало {dice}. Вы выиграли {profit}💰!")
    else:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        await update.message.reply_text(f"🎲 Выпало {dice}. Вы проиграли {bet}💰.")
