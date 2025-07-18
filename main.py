import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from flask import Flask
import threading

API_TOKEN = '7615496508:AAFn-YYA9gzAhXCN8zEEdiskTTXMaqMJFto'
ADMIN_ID = 7784034570

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Главная клавиатура
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add("Готовые клады", "Связаться с оператором")

# Клавиатура с граммами
gram_kb = ReplyKeyboardMarkup(resize_keyboard=True)
gram_kb.row("1 грамм", "2 грамма")
gram_kb.row("3 грамма", "4 грамма")
gram_kb.add("5 грамм")

# Flask для пинга
app = Flask(__name__)
@app.route('/')
def home():
    return 'Бот работает'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Старт
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_kb)

# Граммовка
@dp.message_handler(lambda msg: msg.text == "Готовые клады")
async def show_grams(message: types.Message):
    await message.answer("Выберите нужный объём:", reply_markup=gram_kb)

# Ответ на граммы
@dp.message_handler(lambda msg: msg.text in [
    "1 грамм", "2 грамма", "3 грамма", "4 грамма", "5 грамм"
])
async def send_price(message: types.Message):
    prices = {
        "1 грамм": "400.000 VND",
        "2 грамма": "800.000 VND",
        "3 грамма": "1.200.000 VND",
        "4 грамма": "1.600.000 VND",
        "5 грамм": "2.000.000 VND"
    }
    await message.answer(
        f"<b>Цена:</b> {prices[message.text]}\n\n"
        f"<b>USDT-кошелёк:</b>\n<code>TKjjYDJveXkr3Qmk37XraFUnDCoHuAX3zc</code>\n\n"
        "После оплаты пришлите сюда скриншот перевода."
    )

# Оператор
@dp.message_handler(lambda msg: msg.text == "Связаться с оператором")
async def contact(message: types.Message):
    await message.answer("Оператор скоро свяжется с вами. Ожидайте.")

# Фото оплаты
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    caption = (
        f"💸 <b>Платёж от</b> @{message.from_user.username or 'без ника'}\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption)
    await message.answer("Скрин получен! Ожидайте подтверждения от оператора.")

# Запуск
def run_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_bot()
