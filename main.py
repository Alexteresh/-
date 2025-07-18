import os
import asyncio
import logging
from threading import Thread

from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# 📌 Настройки
API_TOKEN = '7615496508:AAFn-YYA9gzAhXCN8zEEdiskTTXMagMJFto'
ADMIN_ID   = 7784034570

# Логи
logging.basicConfig(level=logging.INFO)

# Flask-сервер (Uptime pings)
app = Flask(__name__)
@app.route('/')
def alive():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Запускаем Flask в фоне
Thread(target=run_flask, daemon=True).start()

# Инициализация Aiogram
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище выбора пользователя
user_data: dict[int, dict[str, str]] = {}

# Клавиатуры
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌿 Indica"),
            KeyboardButton(text="🌱 Sativa"),
            KeyboardButton(text="🔀 Hybrid")
        ]
    ],
    resize_keyboard=True
)
amount_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1 грамм"), KeyboardButton(text="2 грамма")],
        [KeyboardButton(text="3 грамма"), KeyboardButton(text="4 грамма")],
        [KeyboardButton(text="5 грамм")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

# /start
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    user_data.pop(message.from_user.id, None)
    await message.answer("Привет, бро! Выбери сорт стаффа 🌿", reply_markup=main_menu)

# Выбор сорта
@dp.message(F.text.in_(["🌿 Indica", "🌱 Sativa", "🔀 Hybrid"]))
async def choose_strain(message: types.Message):
    user_data[message.from_user.id] = {"strain": message.text}
    await message.answer(f"✅ Выбран сорт: {message.text}\nТеперь выбери объём 📋", reply_markup=amount_menu)

# Назад
@dp.message(F.text == "⬅️ Назад")
async def go_back(message: types.Message):
    user_data.pop(message.from_user.id, None)
    await message.answer("Возвращаемся в главное меню 🌿", reply_markup=main_menu)

# Выбор объёма
@dp.message(F.text.in_(["1 грамм", "2 грамма", "3 грамма", "4 грамма", "5 грамм"]))
async def choose_amount(message: types.Message):
    uid = message.from_user.id
    data = user_data.get(uid, {})
    data["amount"] = message.text
    user_data[uid] = data

    prices = {
        "1 грамм": ("400 000 VND", "15.8 USDT"),
        "2 грамма": ("800 000 VND", "31.6 USDT"),
        "3 грамма": ("1 200 000 VND", "47.4 USDT"),
        "4 грамма": ("1 600 000 VND", "63.2 USDT"),
        "5 грамм": ("2 000 000 VND", "78.9 USDT"),
    }
    price_vnd, price_usdt = prices[message.text]

    await message.answer(
        f"✅ Ты выбрал: <b>{message.text}</b>\n"
        f"💸 Стоимость: {price_vnd} (~{price_usdt})\n\n"
        f"Переведи на кошелёк (TRC20):\n"
        f"<code>TKjjYDJveXkr3Qmk37XraFUnDCoHuAX3zc</code>\n\n"
        f"📸 После оплаты пришли сюда скрин чека"
    )

# Обработка скрина оплаты
@dp.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: types.Message):
    uid = message.from_user.id
    data = user_data.get(uid, {})
    strain = data.get("strain", "не указан")
    amount = data.get("amount", "не указан")
    username = message.from_user.username or str(uid)

    caption = (
        f"📥 Оплата от @{username}\n"
        f"🧪 Сорт: {strain}\n"
        f"📦 Объём: {amount}"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption)
    await message.answer("✅ Скрин принят. Оператор свяжется с тобой в ближайшее время.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # В Shell Replit: pip install aiogram==3.7.0 flask
    asyncio.run(main())
