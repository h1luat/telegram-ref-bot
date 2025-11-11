import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
import os

TOKEN = os.getenv("BOT_TOKEN")  # Токен берем из переменных окружения
CHANNEL_ID = "@h1luat_stars"    # Канал, на который нужно быть подписанным

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище рефералов
referrals = {}


# --- Проверка подписки ---
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# --- Главное меню ---
def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 Моя ссылка", callback_data="my_link")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ])
    return keyboard


# --- Старт ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    # Проверяем, есть ли реферальная метка
    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1]
        if ref_id != str(user_id):
            referrals.setdefault(ref_id, set()).add(user_id)

    # Проверка подписки
    if not await is_subscribed(user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton(text="🔄 Проверить подписку", callback_data="check_subscribe")]
        ])
        await message.answer(
            "❌ Вы не подписаны на канал!\n"
            "Подпишитесь на наш канал, чтобы использовать бота:",
            reply_markup=keyboard
        )
        return

    await message.answer("✅ Добро пожаловать! Вы можете использовать бота:", reply_markup=main_menu())


# --- Проверка подписки по кнопке ---
@dp.callback_query(F.data == "check_subscribe")
async def check_subscribe(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text("✅ Подписка подтверждена!", reply_markup=main_menu())
    else:
        await callback.answer("Вы всё ещё не подписаны 😢", show_alert=True)


# --- Моя ссылка ---
@dp.callback_query(F.data == "my_link")
async def send_ref_link(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    ref_link = f"https://t.me/{(await bot.me()).username}?start={user_id}"
    await callback.message.answer(f"📎 Ваша реферальная ссылка:\n{ref_link}")


# --- Профиль ---
@dp.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    refs = len(referrals.get(user_id, []))
    await callback.message.answer(f"👤 Ваш ID: {user_id}\n👥 Приглашено рефералов: {refs}")


# --- Запуск ---
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
