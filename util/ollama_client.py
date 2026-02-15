import datetime
import json
from typing import Literal, Any

from ollama import Client, ResponseError, WebSearchResponse
from pydantic import BaseModel, ValidationError
from retry import retry

from tracker import PostTracker
from util.config import PROMPT_INTERPRETER_FILE, PROMPT_CLASSIFY_FILE, \
    MODEL_INTERPRETER, MODEL_CLASSIFIER, OLLAMA_KEY, MODEL_FIX_LOCATION, PROMPT_FIX_LOCATION_FILE
from util.files_operations import load_file
from util.nominatim import Nominatim


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


class ValidationFunctionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ValidationFunctionMaxTriesError(Exception):
    def __init__(self, message):
        super().__init__(message)


client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + OLLAMA_KEY}
) if OLLAMA_KEY else Client()


def ask(message, model, images=None, temperature: int = 0, tools=None, validate=None, max_validation_tries=2):
    if images is not None and len(images) <= 0:
        images = None

    messages = [{"role": "user", "content": message, "images": images}] if images is not None else [
        {"role": "user", "content": message}]

    return ask_loop(messages, model, temperature, tools, validate, max_validation_tries)


def open_street_map_lookup(query: str) -> list[Any]:
    """Send query directly to open street map and results returned

    Args:
      query: The query to lookup in open street map

    Returns:
      Any results for query as array
    """
    results = Nominatim().query(query, limit=3)
    return [item["display_name"] for item in results]


def web_search_place(place_name: str) -> WebSearchResponse:
    """Search the web for a place

    Args:
      place_name: The place to search for

    Returns:
      Any results
    """
    return client.web_search(f"Address for {place_name}")


available_functions = {
    'open_street_map_lookup': open_street_map_lookup,
    'web_search_place': web_search_place
}


@retry(ResponseError, tries=2, delay=2)
def ask_loop(messages, model, temperature: int = 0, tools=None, validate=None, validation_tries_left=2):
    response = client.chat(
        model=model,
        messages=messages,
        tools=tools,
        options={'temperature': temperature},
    )
    response_content = response.message.content
    messages.append(response.message)
    if response.message.tool_calls and len(response_content) == 0:
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                result = available_functions[tc.function.name](**tc.function.arguments)
                messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
            else:
                messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': "None"})
        return ask_loop(messages, model, temperature, tools, validate, validation_tries_left)
    else:
        if validate is not None:
            try:
                validate(response_content)
            except ValidationFunctionError as e:
                if validation_tries_left == 0:
                    raise ValidationFunctionMaxTriesError(str(e))
                messages.append({"role": "user", "content": f"Result validation failed with error: {str(e)}"})
                return ask_loop(messages, model, temperature, tools, validate, validation_tries_left - 1)
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
            return llm_parse_events(post, max_attempts, attempt + 1)
        else:
            return None, prompt


def validate_llm_fix_location_response(response_to_check):
    if response_to_check is None:
        raise ValidationFunctionError("Response is None.")
    if Nominatim().get_location_details(response_to_check) is None:
        raise ValidationFunctionError("Response does not return valid lookup result.")


def llm_fix_location(event: str):
    prompt = load_ai_prompt(PROMPT_FIX_LOCATION_FILE).replace(
        "{input}", event
    )
    try:
        response = ask(prompt, MODEL_FIX_LOCATION, tools=[open_street_map_lookup, web_search_place],
                       validate=validate_llm_fix_location_response,
                       max_validation_tries=2)
        return response
    except ValidationFunctionMaxTriesError:
        return None


def llm_classify(post: PostTracker):
    prompt = load_ai_prompt(PROMPT_CLASSIFY_FILE).replace(
        "{input}", post.caption() if post.caption() is not None else "None"
    )
    response = ask(prompt, MODEL_CLASSIFIER, images=post.get_image_paths(3))
    return response == "True"
