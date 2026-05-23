import logging
from telegram.ext import Application, CommandHandler
from config import TOKEN
from database import create_pool
from games import roulette, dice, slots, coinflip, blackjack, wheel, lottery
from economy import bank, business, bonus, promo

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    await update.message.reply_text(
        "🎰 Добро пожаловать в казино-бот!\n"
        "Команды: /с, /к, /сл, /мон, /бд, /колесо, /лото, /банк, /бизнес, /бонус, /промо"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    # Регистрируем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("с", roulette.handler))
    app.add_handler(CommandHandler("к", dice.handler))
    app.add_handler(CommandHandler("сл", slots.handler))
    app.add_handler(CommandHandler("мон", coinflip.handler))
    app.add_handler(CommandHandler("бд", blackjack.handler))
    app.add_handler(CommandHandler("колесо", wheel.handler))
    app.add_handler(CommandHandler("лото", lottery.handler))
    app.add_handler(CommandHandler("банк", bank.handler))
    app.add_handler(CommandHandler("бизнес", business.handler))
    app.add_handler(CommandHandler("бонус", bonus.handler))
    app.add_handler(CommandHandler("промо", promo.redeem_handler))
    app.add_handler(CommandHandler("создатьпромо", promo.create_handler))
    # Запускаем
    app.run_polling()

if __name__ == "__main__":
    main()
