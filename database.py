import asyncpg
from datetime import datetime, timezone
from config import DATABASE_URL

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def get_user(pool, user_id: int):
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
        if not user:
            now = datetime.now(timezone.utc)
            await conn.execute(
                "INSERT INTO users(user_id, balance, last_bank_interest) VALUES($1, 1000, $2)",
                user_id, now
            )
            user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
        return dict(user)

async def update_balance(pool, user_id: int, amount: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE user_id=$2",
            amount, user_id
        )

async def add_transaction(pool, user_id: int, ttype: str, amount: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO transactions(user_id, type, amount, balance_after) "
            "VALUES($1, $2, $3, (SELECT balance FROM users WHERE user_id=$1))",
            user_id, ttype, amount
        )

async def get_business_count(pool, user_id: int):
    return await pool.fetchval(
        "SELECT COUNT(*) FROM businesses WHERE user_id=$1", user_id
    )

async def create_business(pool, user_id: int, name: str, daily_income: int):
    await pool.execute(
        "INSERT INTO businesses(user_id, name, daily_income) VALUES($1,$2,$3)",
        user_id, name, daily_income
    )

async def get_user_businesses(pool, user_id: int):
    return await pool.fetch(
        "SELECT id, name, daily_income, last_collected FROM businesses WHERE user_id=$1",
        user_id
    )

async def update_business_last_collected(pool, business_id: int, ts):
    await pool.execute(
        "UPDATE businesses SET last_collected=$1 WHERE id=$2",
        ts, business_id
    )

async def create_promo(pool, code: str, amount: int, creator: int):
    await pool.execute(
        "INSERT INTO promo_codes(code, amount, created_by) VALUES($1,$2,$3) ON CONFLICT DO NOTHING",
        code, amount, creator
    )

async def get_promo(pool, code: str):
    return await pool.fetchrow("SELECT * FROM promo_codes WHERE code=$1", code)

async def use_promo(pool, code: str, used_by: int):
    await pool.execute(
        "UPDATE promo_codes SET used=TRUE, used_by=$1 WHERE code=$2",
        used_by, code
    )
