import datetime
import json
from typing import Literal

from ollama import Client
from pydantic import BaseModel

from tracker import PostTracker
from util.config import PROMPT_INTERPRETER_FILE, PROMPT_CLASSIFY_FILE, \
    MODEL_INTERPRETER, MODEL_CLASSIFIER
from util.files_operations import load_file


class Location(BaseModel):
    type: Literal['Hybrid', 'Online', 'Offline', 'Unknown']
    offline_address: str | None
    online_link: str | None


class Event(BaseModel):
    title: str
    type: Literal[
        'Demo', 'Konzert', 'Konferenz', 'Camp', 'Aktion', 'Festival', 'Diskussion', 'Workshop', 'Jahrestag', 'Anderes']
    location: Location
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    description: str
    link: str


class Events(BaseModel):
    events: list[Event]


client = Client()


def ask(message, model, images=None):
    if images is not None and len(images) <= 0:
        images = None
    messages = [{"role": "user", "content": message, "images": images}] if images is not None else [
        {"role": "user", "content": message}]

    response = client.chat(
        model=model,
        messages=messages,
        options={'temperature': 0},
    )
    response_content = response.message.content
    messages.append({"role": "assistant", "content": response_content})
    return response_content


def load_ai_prompt(file_path):
    return load_file(file_path)


def llm_parse_events(post: PostTracker):
    prompt = load_ai_prompt(PROMPT_INTERPRETER_FILE).replace(
        "{input}", post.caption()
    ).replace(
        "{owner_link}", post.account_details.link
    ).replace(
        "{owner_name}", post.account_details.name
    ).replace(
        "{owner_bio}", post.account_details.bio
    ).replace(
        "{scheme}", json.dumps(Events.model_json_schema(), indent=2)
    ).replace("{year}", f"{post.date.year}")

    response = ask(prompt, MODEL_INTERPRETER, images=post.get_image_paths(3))
    parsed = response.replace("```json", "").replace("```", "")

    if Events.model_validate_json(response):
        return json.loads(parsed), prompt
    else:
        return None


def llm_classify(post: PostTracker):
    prompt = load_ai_prompt(PROMPT_CLASSIFY_FILE).replace(
        "{input}", post.caption()
    )
    response = ask(prompt, MODEL_CLASSIFIER, images=post.get_image_paths(3))
    return response == "True"
