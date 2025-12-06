import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Токен бота (установи через переменную окружения BOT_TOKEN)
TOKEN = getenv("6600994228:AAEKvdJCVZPCBXkP3ylfFW9jHqS-l0U1WPo")

# Проверка токена
if TOKEN is None:
    print("❌ ОШИБКА: Токен бота не найден!")
    print("Установите переменную окружения BOT_TOKEN")
    sys.exit(1)

# Создаем диспетчер
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Приветственное сообщение с HTML-разметкой и кнопкой
    """
    # Создаем клавиатуру с одной кнопкой
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛒 Открыть Маркет")
    
    # Текст сообщения с HTML-разметкой
    welcome_text = (
        html.bold("🌟 Добро пожаловать в наш магазин!") + "\n\n" +
        html.bold("✨ Здесь вы можете:") + "\n" +
        "• 🛍️ " + html.italic("Просматривать каталог товаров") + "\n" +
        "• 🔥 " + html.italic("Участвовать в акциях") + "\n" +
        "• 📦 " + html.italic("Отслеживать свои заказы") + "\n" +
        "• 💰 " + html.italic("Копить бонусы") + "\n" +
        "• 🚚 " + html.italic("Заказывать доставку") + "\n\n" +
        html.bold("Нажмите кнопку ") + html.code("Открыть Маркет") +
        html.bold(" и совершите свою первую покупку!")
    )
    
    # Отправляем сообщение с клавиатурой
    await message.answer(
        welcome_text,
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Простой эхо-обработчик для других сообщений
@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Простой эхо-ответ
    """
    if message.text:
        await message.answer(f"Вы написали: {html.quote(message.text)}")

async def main() -> None:
    # Инициализируем бота с HTML-парсингом по умолчанию
    bot = Bot(
        token=TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    print("🤖 Бот запущен...")
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("bot.log")
        ]
    )
    
    try:
        # Запускаем бота
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
