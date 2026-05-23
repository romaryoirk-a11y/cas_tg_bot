import random
from datetime import datetime, timezone
from database import get_user, update_balance, add_transaction, get_business_count, create_business, get_user_businesses, update_business_last_collected

MAX_BUSINESSES = 5
COLLECT_COOLDOWN = 24 * 3600

async def list_businesses(update, context):
    user_id = update.effective_user.id
    pool = context.bot_data["pool"]
    businesses = await get_user_businesses(pool, user_id)
    if not businesses:
        await update.message.reply_text("У вас пока нет бизнесов. Создайте: /бизнес создать <название>")
        return
    now = datetime.now(timezone.utc)
    msg = "🏢 Ваши бизнесы:\n"
    for b in businesses:
        delta = (now - b["last_collected"]).total_seconds()
        if delta >= COLLECT_COOLDOWN:
            status = "✅ Можно собрать"
        else:
            hours = int((COLLECT_COOLDOWN - delta) // 3600)
            mins = int(((COLLECT_COOLDOWN - delta) % 3600) // 60)
            status = f"⏳ {hours}ч {mins}м"
        msg += f"{b['id']}. {b['name']} — {b['daily_income']}💰/день ({status})\n"
    await update.message.reply_text(msg)

async def create_business_cmd(update, context):
    user_id = update.effective_user.id
    pool = context.bot_data["pool"]
    count = await get_business_count(pool, user_id)
    if count >= MAX_BUSINESSES:
        await update.message.reply_text(f"❌ Можно иметь не более {MAX_BUSINESSES} бизнесов.")
        return
    name = " ".join(context.args) if context.args else "Бизнес"
    income = random.randint(100, 1000)
    await create_business(pool, user_id, name, income)
    await update.message.reply_text(f"✅ Бизнес «{name}» создан! Доход: {income}💰/день.")

async def collect_income_cmd(update, context):
    user_id = update.effective_user.id
    pool = context.bot_data["pool"]
    businesses = await get_user_businesses(pool, user_id)
    now = datetime.now(timezone.utc)
    total = 0
    collected = []
    for b in businesses:
        if (now - b["last_collected"]).total_seconds() >= COLLECT_COOLDOWN:
            await update_business_last_collected(pool, b["id"], now)
            total += b["daily_income"]
            collected.append(f"{b['name']} (+{b['daily_income']})")
    if total == 0:
        await update.message.reply_text("Пока нечего собирать. Доход можно получать раз в 24 часа.")
        return
    await update_balance(pool, user_id, total)
    await add_transaction(pool, user_id, "business_income", total)
    await update.message.reply_text(f"💸 Собрано: {total}💰\n" + "\n".join(collected))

async def handler(update, context):
    args = context.args
    if not args:
        await list_businesses(update, context)
        return
    sub = args[0].lower()
    if sub == "создать":
        context.args = args[1:]  # остальное — название
        await create_business_cmd(update, context)
    elif sub == "собрать":
        await collect_income_cmd(update, context)
    else:
        await list_businesses(update, context)
