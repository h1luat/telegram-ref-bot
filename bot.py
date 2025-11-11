import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

BOT_TOKEN = "8172728168:AAGf4IT93SBii_9mhg2KQMMR07llcDuYz1E"

# База данных
conn = sqlite3.connect("referrals.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referred_by INTEGER,
    referrals INTEGER DEFAULT 0
)
""")
conn.commit()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Функция генерации клавиатуры ---
def main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 Моя ссылка", callback_data="my_link")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ])
    return keyboard

# --- /start ---
@dp.message(Command("start"))
async def start(message: types.Message):
    args = message.text.split()
    referrer = None
    if len(args) > 1 and args[1].isdigit():
        referrer = int(args[1])

    cur.execute("SELECT * FROM users WHERE user_id = ?", (message.from_user.id,))
    user = cur.fetchone()

    if not user:
        cur.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (message.from_user.id, referrer))
        conn.commit()

        if referrer:
            cur.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id = ?", (referrer,))
            conn.commit()
            try:
                await bot.send_message(referrer, f"🎉 У тебя новый реферал: {message.from_user.full_name}")
            except:
                pass

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Используй кнопки ниже 👇",
        reply_markup=main_keyboard()
    )

# --- Обработчик кнопки "Моя ссылка" ---
@dp.callback_query(F.data == "my_link")
async def send_ref_link(callback: types.CallbackQuery):
    bot_user = await bot.get_me()
    ref_link = f"https://t.me/{bot_user.username}?start={callback.from_user.id}"
    await callback.message.answer(f"📎 Твоя реферальная ссылка:\n{ref_link}")

# --- Обработчик кнопки "Профиль" ---
@dp.callback_query(F.data == "profile")
async def send_profile(callback: types.CallbackQuery):
    cur.execute("SELECT referrals FROM users WHERE user_id = ?", (callback.from_user.id,))
    row = cur.fetchone()
    count = row[0] if row else 0
    await callback.message.answer(
        f"👤 Твой профиль:\n\n"
        f"🆔 Telegram ID: `{callback.from_user.id}`\n"
        f"👥 Количество рефералов: {count}",
        parse_mode="Markdown"
    )

# --- Команда /profile (если вводит вручную) ---
@dp.message(Command("profile"))
async def profile_command(message: types.Message):
    cur.execute("SELECT referrals FROM users WHERE user_id = ?", (message.from_user.id,))
    row = cur.fetchone()
    count = row[0] if row else 0
    await message.answer(
        f"👤 Твой профиль:\n\n"
        f"🆔 Telegram ID: `{message.from_user.id}`\n"
        f"👥 Количество рефералов: {count}",
        parse_mode="Markdown"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
