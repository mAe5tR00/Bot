import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
import pandas as pd

API_TOKEN = '6600994228:AAEKvdJCVZPCBXkP3ylfFW9jHqS-l0U1WPo'
ADMIN_ID = 5470301151
CHANNEL_ID = "@notcryptonian"  # Ваш канал в формате @your_channel_id
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT"
KLINE_API_URL = "https://api.binance.com/api/v3/klines?symbol={coin}USDT&interval=1h"
SLEEP_INTERVAL = 900  # 15 минут в секундах

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(storage=MemoryStorage())

# Глобальные переменные для хранения отслеживаемой монеты и предыдущих данных
monitored_coin = None
previous_trend = None
previous_buy_volume = None
previous_sell_volume = None
previous_support_level = None
previous_resistance_level = None

def get_start_keyboard():
    """Создание стартовой клавиатуры."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Установить монету", callback_data="set_coin")
    return builder.as_markup()

def get_status_keyboard():
    """Создание клавиатуры для проверки статуса."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Проверить статус", callback_data="status")
    return builder.as_markup()

@dp.message(Command(commands=['start']))
async def start_command(message: Message):
    """Обработчик команды /start."""
    await message.answer(
        "Здравствуйте! Я ваш бот для мониторинга криптовалют. Управлять ботом может только администратор.",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(lambda c: c.data == 'set_coin')
async def set_coin_callback(callback_query: CallbackQuery):
    """Обработчик нажатия на кнопку 'Установить монету'."""
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("У вас нет прав для выполнения этой команды.")
        return
    await callback_query.message.answer("Пожалуйста, введите символ монеты для отслеживания. Например, BTC")
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == 'status')
async def status_callback(callback_query: CallbackQuery):
    """Обработчик нажатия на кнопку 'Проверить статус'."""
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("У вас нет прав для выполнения этой команды.")
        return
    if not monitored_coin:
        await callback_query.message.answer("Монета для отслеживания не установлена.")
    else:
        await send_coin_status(callback_query.message)
    await callback_query.answer()

@dp.message()
async def handle_message(message: Message):
    """Обработчик входящих сообщений."""
    global monitored_coin
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    monitored_coin = message.text.strip().upper()
    await message.answer(f"Монета для отслеживания установлена: {monitored_coin}")
    await send_coin_status(message)

async def send_coin_status(message: Message):
    """Отправка текущего статуса монеты в канал."""
    coin_data = get_coin_data(monitored_coin)
    if coin_data:
        buy_volume = int(float(coin_data['buy_volume']))
        sell_volume = int(float(coin_data['sell_volume']))
        total_volume = buy_volume + sell_volume
        buy_percentage = (buy_volume / total_volume) * 100
        sell_percentage = (sell_volume / total_volume) * 100
        trend_emoji = "📈" if coin_data['trend'] == "Восходящий" else "📉"

        # Определение зон поддержки и сопротивления с помощью pandas
        close_prices = [float(price) for price in coin_data['close_prices']]
        df = pd.DataFrame(close_prices, columns=['close'])
        support_level = df['close'].rolling(window=20).min().iloc[-1]
        resistance_level = df['close'].rolling(window=20).max().iloc[-1]

        response = (
            f"<b>Монета:</b> {monitored_coin}\n"
            f"<b>Цена:</b> {coin_data['price']}\n"
            f"<b>Объем (Покупка):</b> {buy_percentage:.2f}%\n"
            f"<b>Объем (Продажа):</b> {sell_percentage:.2f}%\n"
            f"<b>Тренд:</b> {coin_data['trend']} {trend_emoji}\n"
            f"<b>Зона поддержки:</b> {support_level}\n"
            f"<b>Зона сопротивления:</b> {resistance_level}"
        )
        await bot.send_message(CHANNEL_ID, response, reply_markup=get_status_keyboard())
    else:
        await message.answer(f"Не удалось получить данные для монеты {monitored_coin}.")


async def monitor_coin():
    """Мониторинг статуса монеты с регулярными интервалами."""
    global previous_trend, previous_buy_volume, previous_sell_volume, previous_support_level, previous_resistance_level
    while True:
        if monitored_coin:
            coin_data = get_coin_data(monitored_coin)
            if coin_data:
                current_trend = coin_data['trend']
                current_buy_volume = int(float(coin_data['buy_volume']))
                current_sell_volume = int(float(coin_data['sell_volume']))
                close_prices = [float(price) for price in coin_data['close_prices']]
                df = pd.DataFrame(close_prices, columns=['close'])
                support_level = df['close'].rolling(window=20).min().iloc[-1]
                resistance_level = df['close'].rolling(window=20).max().iloc[-1]

                # Формирование сообщения о статусе
                response = (
                    f"<b>Монета:</b> {monitored_coin}\n"
                    f"<b>Цена:</b> {coin_data['price']}\n"
                    f"<b>Зона поддержки:</b> {support_level}\n"
                    f"<b>Зона сопротивления:</b> {resistance_level}"
                )

                # Проверка изменений и отправка сообщений
                if (
                        current_trend != previous_trend or
                        current_buy_volume != previous_buy_volume or
                        current_sell_volume != previous_sell_volume or
                        support_level != previous_support_level or
                        resistance_level != previous_resistance_level
                ):
                    await bot.send_message(CHANNEL_ID, response, reply_markup=get_status_keyboard())
                    previous_trend = current_trend
                    previous_buy_volume = current_buy_volume
                    previous_sell_volume = current_sell_volume
                    previous_support_level = support_level
                    previous_resistance_level = resistance_level
                    logging.info("Notification sent.")
                else:
                    logging.info("No changes, no notification sent.")

        await asyncio.sleep(SLEEP_INTERVAL)  # Ждем 15 минут перед следующей проверкой



def get_coin_data(coin: str):
    """Получение данных о монете с Binance."""
    try:
        # Конечная точка API Binance для получения информации о тикере
        response = requests.get(BINANCE_API_URL.format(coin=coin))
        data = response.json()

        if response.status_code != 200 or 'symbol' not in data:
            return None

        price = data['lastPrice']
        buy_volume = data['volume']
        sell_volume = data['quoteVolume']
        trend = "Восходящий" if float(data['lastPrice']) > float(data['openPrice']) else "Нисходящий"

        # Получение данных о свечах для определения зон поддержки и сопротивления
        kline_response = requests.get(KLINE_API_URL.format(coin=coin))
        kline_data = kline_response.json()

        if kline_response.status_code != 200 or not kline_data:
            return None

        close_prices = [kline[4] for kline in kline_data]  # Цена закрытия каждой свечи

        return {
            "price": price,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "trend": trend,
            "close_prices": close_prices
        }
    except Exception as e:
        logging.error(f"Ошибка при получении данных: {e}")
        return None

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_coin())
    dp.run_polling(bot)
