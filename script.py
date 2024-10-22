import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

VOICEFLOW_API_KEY = os.getenv('VOICEFLOW_API_KEY')


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

    for trace in traces:
        trace_type = trace.get('type')
        if trace_type == 'text' or trace_type == 'speak':
            print("Bot reply:", trace['payload']['message'])
        elif trace_type == 'visual':
            print("Bot sent an image:", trace['payload']['image'])
        elif trace_type == 'end':
            print("Conversation is over")


# Основной цикл взаимодействия через консоль
if __name__ == "__main__":
    chat_id = 12345  # Задай уникальный идентификатор пользователя (вместо Telegram chat ID)

    # Отправка приветственного сообщения (аналог команды /start в Telegram)
    interact(chat_id, {'type': 'launch'})

    while True:
        user_input = input("You: ")  # Считываем сообщение от пользователя из консоли

        if user_input.lower() in ['exit', 'quit']:
            print("Conversation ended.")
            break

        # Отправляем сообщение в Voiceflow API
        interact(chat_id, {
            'type': 'text',
            'payload': user_input
        })
