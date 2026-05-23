import random
from database import update_balance, add_transaction

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("🎟️ !лото <количество билетов> (цена 100💰 за билет)")
        return
    try:
        tickets = int(args[0])
    except ValueError:
        await update.message.reply_text("Количество — число.")
        return
    if tickets <= 0:
        return
    cost = tickets * 100
    pool = context.bot_data["pool"]
    user = await pool.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
    if user["balance"] < cost:
        await update.message.reply_text("Недостаточно средств.")
        return
    # Розыгрыш: шанс на выигрыш ~10% за билет, множитель x10
    total_win = 0
    for _ in range(tickets):
        if random.random() < 0.1:
            total_win += 100 * 10
    await update_balance(pool, user_id, -cost + total_win)
    if total_win > 0:
        await add_transaction(pool, user_id, "game_win", total_win)
        await update.message.reply_text(f"🎟️ Из {tickets} билетов выиграли! Общий выигрыш: {total_win}💰")
    else:
        await add_transaction(pool, user_id, "game_loss", -cost)
        await update.message.reply_text(f"🎟️ Увы, все {tickets} билетов проиграли. Списано {cost}💰.")
