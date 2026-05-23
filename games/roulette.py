import random
from database import update_balance, add_transaction

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("🎰 !с <ставка> <красное/чёрное/число 0-36>")
        return
    try:
        bet = int(args[0])
    except ValueError:
        await update.message.reply_text("Ставка должна быть числом.")
        return
    choice = args[1].lower()
    pool = context.bot_data["pool"]
    user = await pool.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
    if user["balance"] < bet or bet <= 0:
        await update.message.reply_text("Недостаточно средств.")
        return
    number = random.randint(0, 36)
    color = "красное" if number in RED_NUMBERS else "чёрное" if number != 0 else "зеро"
    win = False
    multiplier = 0
    if choice.isdigit() and int(choice) == number:
        win = True
        multiplier = 35
    elif choice == "красное" and color == "красное":
        win = True
        multiplier = 2
    elif choice == "чёрное" and color == "чёрное":
        win = True
        multiplier = 2
    if win:
        profit = bet * multiplier
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        await update.message.reply_text(f"🎡 Выпало {number} ({color}). Выигрыш: {profit}💰")
    else:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        await update.message.reply_text(f"🎡 Выпало {number} ({color}). Проигрыш: {bet}💰")
