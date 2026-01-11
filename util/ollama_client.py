import datetime
import json
from typing import Literal

from ollama import chat
from pydantic import BaseModel

from tracker import PostTracker
from util.config import MODEL_LARGE, MODEL_SMALL, PROMPT_PARSE_FILE, INTERPRETER_USE_OCR, PROMPT_VALUE_FILE, \
    LLM_PASS_IMAGES_DIRECTLY, PROMPT_PARSE_VISION_FILE, MODEL_VISION
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


class EventEval(BaseModel):
    is_event: bool
    confidence: Literal["Very High", "High", "Ok", "Low"]


def ask(message, large_model, format_json=None, images=None):
    if images is not None and len(images) <= 0:
        images = None
    messages = [{"role": "user", "content": message, "images": images}] if images is not None else [
        {"role": "user", "content": message}]
    response = chat(
        model=(MODEL_LARGE if large_model else MODEL_SMALL) if images is None else MODEL_VISION,
        messages=messages,
        format=format_json,
    )
    response_content = response.message.content
    messages.append({"role": "assistant", "content": response_content})
    return response_content


def load_ai_prompt(file_path):
    return load_file(file_path).replace("{year}", f"{datetime.datetime.now().year}")


def llm_parse_events(post: PostTracker):
    prompt_parse = load_ai_prompt(PROMPT_PARSE_VISION_FILE if LLM_PASS_IMAGES_DIRECTLY else PROMPT_PARSE_FILE)
    return json.loads(ask(prompt_parse.replace(
        "{input}", post.caption()
    ).replace(
        "{input_ocr}",
        post.ocr_output()
        if INTERPRETER_USE_OCR
        else "None"
    ).replace(
        "{owner_link}", post.account_details.link
    ).replace(
        "{owner_name}", post.account_details.name)
    .replace(
        "{owner_bio}", post.account_details.bio
    ), True, Events.model_json_schema(), images=post.get_image_paths() if LLM_PASS_IMAGES_DIRECTLY else None))["events"]


def llm_classify(post: PostTracker, large_model):
    classifier_prompt = load_ai_prompt(PROMPT_VALUE_FILE)
    return json.loads(ask(classifier_prompt.replace("{input}", post.caption()).replace(
        "{input_ocr}",
        post.ocr_output()
        if INTERPRETER_USE_OCR
        else "None"
    ), large_model, EventEval.model_json_schema()))
