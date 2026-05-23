import random
from database import update_balance, add_transaction

VALUES = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":10,"Q":10,"K":10,"A":11}
SUITS = ["♠","♥","♦","♣"]

def hand_value(cards):
    total = sum(VALUES[c[0]] for c in cards)
    aces = sum(1 for c in cards if c[0] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def format_hand(cards):
    return " ".join(f"{c[0]}{c[1]}" for c in cards)

async def handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("🃏 !бд <ставка>")
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

    deck = [(v, s) for v in VALUES for s in SUITS]
    random.shuffle(deck)
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]

    # Игрок тянет до 17+
    while hand_value(player) < 17:
        player.append(deck.pop())
    p_val = hand_value(player)
    d_val = hand_value(dealer)
    if p_val > 21:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        await update.message.reply_text(
            f"Ваши карты: {format_hand(player)} ({p_val})\nДилер: {format_hand(dealer)} ({d_val})\nПеребор! Проигрыш {bet}💰."
        )
    elif d_val > 21 or p_val > d_val:
        profit = bet
        await update_balance(pool, user_id, profit)
        await add_transaction(pool, user_id, "game_win", profit)
        await update.message.reply_text(
            f"Ваши карты: {format_hand(player)} ({p_val})\nДилер: {format_hand(dealer)} ({d_val})\nВы выиграли {profit}💰!"
        )
    elif p_val == d_val:
        await update.message.reply_text(
            f"Ваши карты: {format_hand(player)} ({p_val})\nДилер: {format_hand(dealer)} ({d_val})\nНичья. Ставка возвращена."
        )
    else:
        await update_balance(pool, user_id, -bet)
        await add_transaction(pool, user_id, "game_loss", -bet)
        await update.message.reply_text(
            f"Ваши карты: {format_hand(player)} ({p_val})\nДилер: {format_hand(dealer)} ({d_val})\nВы проиграли {bet}💰."
        )
