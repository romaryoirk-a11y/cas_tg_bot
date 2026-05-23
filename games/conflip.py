import random
from database import update_balance, add_transaction

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("🪙 !мон <ставка> <орёл/решка>")
        return
    try:
        bet = int(args[0])
    except ValueError:
        await update.message.reply_text("Ставка — число.")
        return
    choice = args[1].lower()
    if choice not in ("орёл", "орел", "решка"):
        await update.message.reply_text("Выберите 'орёл' или 'решка'.")
        return
    pool = context.bot_data["pool"]
    user = await pool.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
    if user["balance"] < bet or bet <= 0:
        await update.message.reply_text("Недостаточно средств.")
        return
    coin = random.choice(["орёл", "решка"])
    if (choice in ("орёл", "орел") and coin == "орёл") or (choice == "решка" and coin == "решка"):
        profit = bet
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        await update.message.reply_text(f"🪙 {coin.capitalize()}! Вы выиграли {profit}💰.")
    else:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        await update.message.reply_text(f"🪙 {coin.capitalize()}. Вы проиграли {bet}💰.")
