import datetime

from ollama import chat

from config import MODEL_LARGE, MODEL_SMALL
from util.files_operations import load_file


def ask(message, large_model):
    messages = [{"role": "user", "content": message}]
    response = chat(
        model=MODEL_LARGE if large_model else MODEL_SMALL,
        messages=messages,
    )
    response_content = response.message.content
    messages.append({"role": "assistant", "content": response_content})
    return response_content


def load_ai_prompt(file_path):
    return load_file(file_path).replace("{year}", f"{datetime.datetime.now().year}")
