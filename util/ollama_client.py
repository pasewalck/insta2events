import datetime
import json
from typing import Literal

from ollama import Client, ResponseError
from pydantic import BaseModel, ValidationError

from tracker import PostTracker
from util.config import PROMPT_INTERPRETER_FILE, PROMPT_CLASSIFY_FILE, \
    MODEL_INTERPRETER, MODEL_CLASSIFIER, OLLAMA_KEY
from util.files_operations import load_file


class Location(BaseModel):
    type: Literal['Hybrid', 'Online', 'Offline', 'Bundesweit', 'International', 'Unknown']
    offline_address: str | None
    online_link: str | None


class Event(BaseModel):
    title: str
    location: Location | None
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    description: str | None
    link: str | None


class Events(BaseModel):
    events: list[Event]


client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + OLLAMA_KEY}
) if OLLAMA_KEY else Client()


def ask(message, model, images=None, temperature: int = 0):
    if images is not None and len(images) <= 0:
        images = None
    messages = [{"role": "user", "content": message, "images": images}] if images is not None else [
        {"role": "user", "content": message}]

    response = client.chat(
        model=model,
        messages=messages,
        options={'temperature': temperature},
    )
    response_content = response.message.content
    messages.append({"role": "assistant", "content": response_content})
    return response_content


def load_ai_prompt(file_path):
    return load_file(file_path)


def llm_parse_events(post: PostTracker, max_attempts: int = 2, attempt: int = 0):
    prompt = load_ai_prompt(PROMPT_INTERPRETER_FILE).replace(
        "{input}", post.caption() if post.caption() is not None else "None"
    ).replace(
        "{owner_link}", post.account_details.link if post.account_details.link is not None else "None"
    ).replace(
        "{owner_name}", post.account_details.name
    ).replace(
        "{owner_bio}", post.account_details.bio
    ).replace(
        "{scheme}", json.dumps(Events.model_json_schema(), indent=2)
    ).replace("{year}", f"{post.date.year}")

    response = ask(prompt, MODEL_INTERPRETER, images=post.get_image_paths(3), temperature=attempt)
    parsed = response.replace("```json", "").replace("```", "")

    try:
        Events.model_validate_json(parsed)
        return json.loads(parsed), prompt
    except (ValidationError, ResponseError):
        if attempt < max_attempts:
            llm_parse_events(post, max_attempts, attempt + 1)
        else:
            return [], prompt


def llm_classify(post: PostTracker):
    prompt = load_ai_prompt(PROMPT_CLASSIFY_FILE).replace(
        "{input}", post.caption()
    )
    response = ask(prompt, MODEL_CLASSIFIER, images=post.get_image_paths(3))
    return response == "True"
