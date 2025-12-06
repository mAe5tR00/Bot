import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Получаем токен из переменной окружения
TOKEN = os.getenv("6909049704:AAGeTidLhxR7uQoHNlsz4IU9SoD8OW9PMpo")

# Проверяем токен
if not TOKEN:
    print("❌ ОШИБКА: Токен бота не найден!")
    print("Установите переменную окружения BOT_TOKEN")
    sys.exit(1)

# Создаем диспетчер
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message) -> None:
    """
    Приветственное сообщение с кнопкой
    """
    # Создаем клавиатуру
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛒 Открыть Маркет")
    
    # Текст сообщения с HTML разметкой
    welcome_text = (
        "<b>🌟 Добро пожаловать в наш магазин!</b>\n\n"
        "<b>✨ Здесь вы можете:</b>\n"
        "• 🛍️ <i>Просматривать каталог товаров</i>\n"
        "• 🔥 <i>Участвовать в акциях</i>\n"
        "• 📦 <i>Отслеживать свои заказы</i>\n"
        "• 💰 <i>Копить бонусы</i>\n"
        "• 🚚 <i>Заказывать доставку</i>\n\n"
        "Нажмите кнопку <code>Открыть Маркет</code> "
        "и совершите свою первую покупку!"
    )
    
    await message.answer(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Эхо-обработчик
@dp.message()
async def echo_message(message: Message) -> None:
    if message.text:
        await message.answer(f"Вы написали: {message.text}")

async def main() -> None:
    # Инициализируем бота
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    
    print("🤖 Бот запущен и готов к работе...")
    print(f"Bot ID: {(await bot.get_me()).id}")
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Запускаем приложение
    asyncio.run(main())
