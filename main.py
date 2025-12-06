import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

# Получаем токен из переменной окружения
TOKEN = os.getenv("6600994228:AAEKvdJCVZPCBXkP3ylfFW9jHqS-l0U1WPo")

# Проверка токена
if not TOKEN:
    print("❌ ОШИБКА: Токен бота не найден!")
    print("Установите переменную окружения BOT_TOKEN")
    exit(1)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    """
    Приветственное сообщение при команде /start
    """
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
    
    await message.answer(welcome_text)

@dp.message()
async def echo_handler(message: Message):
    """
    Эхо-ответ на все остальные сообщения
    """
    if message.text:
        await message.answer(f"Вы написали: {message.text}")

async def main():
    """
    Основная функция запуска бота
    """
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
