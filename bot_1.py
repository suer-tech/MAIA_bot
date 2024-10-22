import os
import time

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, JobQueue
from datetime import datetime, timedelta

reminder_message_1 = (
    "Как у вас дела? Надеюсь, наше общение вам пока нравится. Если есть вопросы или что-то непонятно, я всегда готова помочь.\n"
)

reminder_message_2 = (
    "Все ли вам понятно в ходе нашего общения? Если потребуется моя помощь или помощь менеджера, дайте знать — я здесь, чтобы сделать процесс максимально удобным и эффективным!"
)


# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем API ключи из .env файла
VOICEFLOW_API_KEY = os.getenv('VOICEFLOW_API_KEY')
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')

# Словарь для хранения времени последнего сообщения для каждого пользователя
last_message_time = {}


# Функция для взаимодействия с Voiceflow API
def interact(chat_id, request):
    url = f"https://general-runtime.voiceflow.com/state/user/{chat_id}/interact"
    headers = {
        'Authorization': VOICEFLOW_API_KEY
    }
    data = {
        'request': request
    }

    response = requests.post(url, headers=headers, json=data)
    traces = response.json()

    reply_messages = []
    for trace in traces:
        trace_type = trace.get('type')
        if trace_type == 'text' or trace_type == 'speak':
            reply_messages.append(trace['payload']['message'])
        elif trace_type == 'visual':
            reply_messages.append(f"Bot sent an image: {trace['payload']['image']}")
        elif trace_type == 'end':
            reply_messages.append("Conversation is over")
    return "\n".join(reply_messages)


# Функция для отправки напоминания через 5 минут
async def send_reminder(context):
    job = context.job
    chat_id = job.data
    await context.bot.send_message(chat_id=chat_id, text=reminder_message_1)
    time.sleep(10)
    await context.bot.send_message(chat_id=chat_id, text=reminder_message_2)


# Обработчик команды /start
async def start(update: Update, context):
    chat_id = update.message.chat_id
    # Отправка приветственного сообщения в Voiceflow
    bot_reply = interact(chat_id, {'type': 'launch'})
    if bot_reply:
        await update.message.reply_text(bot_reply)

    # Запоминаем текущее время
    last_message_time[chat_id] = datetime.now()

    # Планируем отправку сообщения через 5 минут
    context.job_queue.run_once(send_reminder, 72000, data=chat_id)


# Обработчик текстовых сообщений
async def handle_message(update: Update, context):
    user_input = update.message.text
    chat_id = update.message.chat_id

    # Отправка сообщения в Voiceflow
    bot_reply = interact(chat_id, {'type': 'text', 'payload': user_input})

    if bot_reply:
        await update.message.reply_text(bot_reply)

    # Обновляем время последнего сообщения
    last_message_time[chat_id] = datetime.now()

    # Проверка и отмена предыдущих задач для пользователя, если они есть
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()

    # Планируем новое напоминание через 20 часов
    context.job_queue.run_once(send_reminder, 72000, data=chat_id, name=str(chat_id))


# Основная функция для запуска бота
if __name__ == "__main__":
    # Инициализируем приложение с JobQueue
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Команда /start
    app.add_handler(CommandHandler("start", start))

    # Обработка всех текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота с JobQueue для управления заданиями
    app.run_polling()
