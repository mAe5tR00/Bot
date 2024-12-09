from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from wcwidth import wcswidth
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, JobQueue
import requests

# ID администратора
ADMIN_ID = 5470301151  # Замените на реальный ID администратора
GROUP_CHAT_ID = -1001974128304  # Замените на ID вашей группы

# API-ключ Clash of Clans
with open('clash.txt', 'r') as file:
    API_KEY = file.read().strip()
CLAN_TAG = '#2PG9LRVJJ'


# Функция для получения информации о клане
def get_clan_info():
    url = f'https://api.clashofclans.com/v1/clans/{CLAN_TAG.replace("#", "%23")}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Функция для получения топ-10 донатеров
async def top_donors(context: CallbackContext) -> None:
    clan_data = get_clan_info()
    if clan_data and 'memberList' in clan_data:
        members = clan_data['memberList']

        # Сортируем участников по донатам
        sorted_members = sorted(members, key=lambda x: x['donations'], reverse=True)[:10]

        # Определяем максимальную ширину столбцов с учетом реальной ширины символов
        max_name_len = max(wcswidth(member['name']) for member in sorted_members)
        max_tag_len = max(len(member['tag']) for member in sorted_members)
        max_donations_len = max(len(str(member['donations'])) for member in sorted_members)

        # Заголовок таблицы
        info = (
            "🏆 *Топ 10 участников по донату:*\n\n"
            f"| {'№':<3} | {'Имя':<{max_name_len}} | {'Тег':<{max_tag_len}} | {'Донат':<{max_donations_len}} |\n"
            f"|{'-'*4}|{'-'*(max_name_len+2)}|{'-'*(max_tag_len+2)}|{'-'*(max_donations_len+2)}|\n"
        )

        # Формируем строки для участников
        for idx, member in enumerate(sorted_members, start=1):
            name = member['name']
            tag = member['tag']
            donations = member['donations']
            # Используем wcswidth для правильного выравнивания по ширине
            info += f"| {idx:<3} | {name:<{max_name_len}} | `{tag:<{max_tag_len}}` | {donations:<{max_donations_len}} |\n"

        # Отправляем сообщение
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"```\n{info}\n```", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="❌ Не удалось получить данные о клане.", parse_mode="Markdown")


# Команда для получения информации о членах клана
async def members_info(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_ID:
        return

    clan_data = get_clan_info()
    if clan_data and 'memberList' in clan_data:
        members = clan_data['memberList']

        # Заголовок таблицы
        info = (
            "👥 *Участники клана:*\n\n"
            "| Имя                | Тег           | Трофеи  | Уровень  | Донат   | Получено |\n"
            "|--------------------|---------------|---------|----------|---------|----------|\n"
        )

        # Формируем строки для участников
        for member in members:
            name = member['name'][:18]  # Ограничиваем имя до 18 символов
            tag = member['tag']
            trophies = member['trophies']
            level = member['expLevel']
            donations = member['donations']
            received = member['donationsReceived']

            # Форматируем строку
            info += f"| {name:<18} | {tag:<13} | {trophies:<7} | {level:<8} | {donations:<7} | {received:<8} |\n"

        # Разбиваем длинные сообщения на части
        messages = []
        while len(info) > 4000:  # Если длина текста превышает 4000 символов
            split_index = info.rfind("\n", 0, 4000)  # Ищем последнее разделение по строке
            messages.append(info[:split_index])
            info = info[split_index + 1:]

        # Добавляем оставшийся текст
        if info:
            messages.append(info)

        # Отправляем каждую часть
        for msg in messages:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"```\n{msg}\n```", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Не удалось получить список участников.", parse_mode="Markdown")


# Команда /claninfo
async def clan_info(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_ID:
        return

    clan_data = get_clan_info()

    if clan_data:
        info = (
            f"🏰 *Название клана:* {clan_data['name']}\n"
            f"🔖 *Тег клана:* `{clan_data['tag']}`\n"
            f"👥 *Участники:* {clan_data['members']}/50\n"
            f"🏆 *Кубки клана:* {clan_data['clanPoints']}\n"
            f"📈 *Уровень клана:* {clan_data['clanLevel']}\n"
        )

        await context.bot.send_message(chat_id=update.effective_chat.id, text=info, parse_mode="Markdown")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Ошибка:* Не удалось получить данные о клане. Проверьте настройки API.",
            parse_mode="Markdown"
        )


# Команда /start с кнопками
async def start(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("Информация о клане", callback_data='clan_info')],
        [InlineKeyboardButton("Участники", callback_data='members_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите действие:", reply_markup=reply_markup)


# Обработчик нажатий кнопок
async def button_handler(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != ADMIN_ID:
        return

    query = update.callback_query
    await query.answer()

    if query.data == 'clan_info':
        await clan_info(update, context)
    elif query.data == 'members_info':
        await members_info(update, context)


# Запуск бота
def main():
    application = Application.builder().token("6521854767:AAEo3OJ_7S3hCcbpGBxeoxh-TdjUo-ihRN0").build()

    # Планировщик для отправки топ-10 донатеров каждый час
    job_queue = application.job_queue
    job_queue.run_repeating(top_donors, interval=3600, first=10)  # Проверять каждые 3600 секунд (1 час)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("claninfo", clan_info))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


if __name__ == '__main__':
    main()
