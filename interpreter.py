import datetime
import os
import re

from numpy.f2py.auxfuncs import throw_error
from ollama import chat

from config import MODEL_LARGE, MODEL_SMALL, PROMPT_OCR_PARSE_FILE, PROMPT_VALUE_FILE, DATA_PARENT_FOLDER, \
    INTERPRETER_USE_OCR, \
    PROMPT_PARSE_FILE, POSTS_FOLDER_NAME, OCR_OUTPUT_FILE_NAME, LLM_OUTPUT_FILE_NAME, INTERPRETER_CLASSIFIER_MODE, \
    RERUN_INTERPRETER, IMPROVE_OCR_WITH_LLM
from tracker import use_tracker, PostTracker
from util.files_operations import load_file, write_json

# Load prompts
prompt_ocr_parse = load_file(PROMPT_OCR_PARSE_FILE)
prompt_value = load_file(PROMPT_VALUE_FILE)
prompt_parse = load_file(PROMPT_PARSE_FILE)

# Lists of keywords in English and German
english_keywords = [
    'event', 'festival', 'concert', 'party', 'celebration',
    'gathering', 'exhibition', 'launch', 'ceremony', 'workshop',
    'conference', 'meetup', 'gala', 'opening', 'show'
]
german_keywords = [
    'ereignis', 'festival', 'konzert', 'party', 'feier',
    'zusammenkunft', 'ausstellung', 'einführung', 'zeremonie', 'workshop',
    'konferenz', 'treffen', 'gala', 'eröffnung', 'show', 'aktion'
]
english_weekdays = [
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
]
german_weekdays = [
    'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag'
]

english_months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december"]
german_months = ["januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober",
                 "november", "dezember"]

# Dates Pattern (format: DD.MM.YYYY or other similar formats)
date_pattern = r'\d{1,2}[.\-\/][ ]\d{1,2}[.\-\/]'


def match_text(text):
    contains = False
    for word in (
            english_keywords + german_keywords + english_weekdays + german_weekdays + german_months + english_months):
        if word.lower() in text.lower():
            contains = True
    match = re.search(date_pattern, text, re.IGNORECASE)
    if (match is not None and match.group() != "") or contains:
        return True
    else:
        return False


def ask(message, large_model):
    messages = [{"role": "user", "content": message}]
    response = chat(
        model=MODEL_LARGE if large_model else MODEL_SMALL,
        messages=messages,
    )
    response_content = response.message.content
    messages.append({"role": "assistant", "content": response_content})
    return response_content


def evaluate_content(content):
    evaluation = ask(content, False)
    return evaluation


def parse_content(content):
    return ask(content, True)


def check_file_exists(file_path):
    return os.path.isfile(file_path)


def main():
    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            print(post.media_id)
            if not post.interpreted or RERUN_INTERPRETER:
                run_interpreter(post)
                post.interpreted = True


def run_interpreter(post: PostTracker):
    directory = os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{post.media_id}")

    content_caption = load_file(os.path.join(directory, "data.txt"), None)
    content_ocr_raw = load_file(os.path.join(directory, OCR_OUTPUT_FILE_NAME), "None")
    use_ocr = INTERPRETER_USE_OCR and content_ocr_raw is not None

    seems_to_be_event = classifier(content_caption) or (use_ocr and classifier(content_ocr_raw))

    print(f"Evaluation for {post.media_id}: {seems_to_be_event}")

    if seems_to_be_event:
        input_ocr = (ask(prompt_ocr_parse.replace("{input}", content_ocr_raw),
                         False) if IMPROVE_OCR_WITH_LLM else content_ocr_raw) if use_ocr else "None"
        result = parse_content(
            prompt_parse.replace("{input}", content_caption).replace("{input_ocr}", input_ocr).replace(
                "{owner_link}", post.account_details.link).replace(
                "{owner_name}", post.account_details.name).replace("{owner_bio}", post.account_details.bio))
        print(f"Parsed: {result}" if result != [] and result != "[]" else f"Parse failed!")
    else:
        result = []

    write_json(os.path.join(directory, LLM_OUTPUT_FILE_NAME), result)


def classifier(content):
    if INTERPRETER_CLASSIFIER_MODE == "basic":
        return match_text(content)
    elif INTERPRETER_CLASSIFIER_MODE == "llm":
        return ai_classifier(content)
    else:
        throw_error("No Interpreter Mode")


def ai_classifier(content):
    return evaluate_content(prompt_value.replace("{input}", content)) == "true"


if __name__ == "__main__":
    main()


def load_ai_prompt(file_path):
    return load_file(file_path).replace("{year}", f"{datetime.datetime.now().year}")
