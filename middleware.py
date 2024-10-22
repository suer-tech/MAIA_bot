import os
import requests
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загружаем переменные окружения из .env файла
load_dotenv()

VOICEFLOW_API_KEY = os.getenv('VOICEFLOW_API_KEY')


class VoiceflowMiddleware:
    def __init__(self):
        self.chat_id = None

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def interact(self, request):
        url = f"https://general-runtime.voiceflow.com/state/user/{self.chat_id}/interact"
        headers = {
            'Authorization': VOICEFLOW_API_KEY
        }
        data = {
            'request': request
        }

        response = requests.post(url, headers=headers, json=data)

        # Проверка успешности запроса
        if response.status_code != 200:
            logging.error(f"Error {response.status_code}: {response.text}")
            return []  # Вернем пустой список в случае ошибки

        return response.json()

    def handle_user_message(self, message):
        if self.chat_id is None:
            raise ValueError("Chat ID is not set.")

        request = {
            'type': 'text',
            'payload': message
        }

        return self.interact(request)

    def launch_conversation(self):
        if self.chat_id is None:
            raise ValueError("Chat ID is not set.")

        request = {
            'type': 'launch'
        }

        return self.interact(request)
