"""Ответы AI-помощника (Azure AI Inference)."""

import re

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from django.conf import settings

# Что делает: Удаляет из ответа AI блоки <think>...</think>.
_THINKING_RE = re.compile(
    r"<think>[\s\S]*?</think>", re.IGNORECASE
)


def sanitize_ai_output(text: str) -> str:
    if not text:
        return ""
    return _THINKING_RE.sub("", text).strip()

# build_ai_messages() — собирает историю чата
def build_ai_messages(room, user_text: str) -> list[dict]:
    system_prompt = getattr(settings, "AI_CHAT_SYSTEM_PROMPT", "").strip()  
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    history = list(room.messages.order_by("-created_at")[:10])
    history.reverse()
    for item in history:
        role = "assistant" if item.sender_role == "ai_assistant" else "user"
        messages.append({"role": role, "content": item.text})
    messages.append({"role": "user", "content": user_text})
    return messages

#   generate_ai_reply() — отправляет запрос в Azure AI

def generate_ai_reply(room, user_text: str) -> str:
   
#    getattr(объект, "имя_атрибута", значение_по_умолчанию) 
#    Встроенная функция Python. Безопасно получает атрибут объекта. Не падает, если атрибута нет.



    if not getattr(settings, "AI_CHAT_ENABLED", False):
        return "AI-чат временно отключен в конфигурации сервиса."

    token = getattr(settings, "AI_CHAT_TOKEN", "").strip()
    endpoint = getattr(settings, "AI_CHAT_ENDPOINT", "").strip()
    model = getattr(settings, "AI_CHAT_MODEL", "").strip()
    if not token or not endpoint or not model:
        return "AI не настроен: отсутствуют AI_CHAT_TOKEN / AI_CHAT_ENDPOINT / AI_CHAT_MODEL."
   
    # 2. Создаём клиент

    client = ChatCompletionsClient(
        endpoint=endpoint, credential=AzureKeyCredential(token)
    )
    response = client.complete(
        messages=build_ai_messages(room, user_text),
        model=model,
        max_tokens=1024,  # максимум 1024 токена (~700 слов)

    )    # 4. Забираем ответ

    content = response.choices[0].message.content if response.choices else ""
    # 5. Чистим от <think>...</think>

    cleaned = sanitize_ai_output(content)
    return cleaned or "Не удалось получить содержательный ответ. Попробуйте уточнить запрос."
