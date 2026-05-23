from database import get_promo, create_promo, use_promo, update_balance, add_transaction
from config import ADMIN_IDS

async def create_handler(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Использование: /создатьпромо <код> <сумма>")
        return
    code, amount = args[0], int(args[1])
    pool = context.bot_data["pool"]
    await create_promo(pool, code, amount, user_id)
    await update.message.reply_text(f"Промокод {code} на {amount}💰 создан.")

async def redeem_handler(update, context):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /промо <код>")
        return
    code = args[0]
    pool = context.bot_data["pool"]
    promo = await get_promo(pool, code)
    if not promo or promo["used"]:
        await update.message.reply_text("❌ Неверный или уже использованный промокод.")
        return
    await use_promo(pool, code, user_id)
    await update_balance(pool, user_id, promo["amount"])
    await add_transaction(pool, user_id, "promo", promo["amount"])
    await update.message.reply_text(f"🎉 Промокод активирован! +{promo['amount']}💰")
