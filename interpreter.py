import datetime
import os

from ollama import chat

from config import MODEL_LARGE, MODEL_SMALL, PROMPT_OCR_PARSE_FILE, PROMPT_VALUE_FILE, DATA_PARENT_FOLDER, LLM_USE_OCR, \
    PROMPT_PARSE_FILE, POSTS_FOLDER_NAME, OCR_OUTPUT_FILE_NAME, LLM_OUTPUT_FILE_NAME
from tracker import use_tracker, PostTracker
from util.files_operations import load_file, load_json, write_json

# Load prompts
prompt_ocr_parse = load_file(PROMPT_OCR_PARSE_FILE)
prompt_value = load_file(PROMPT_VALUE_FILE)
prompt_parse = load_file(PROMPT_PARSE_FILE)


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

        for post in sync_tracker.posts:
            if not post.interpreted:
                run_interpreter(post)
                post.interpreted = True


def run_interpreter(post: PostTracker):
    directory = os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{post.media_id}")

    content_caption = load_file(os.path.join(directory, "data.txt"))
    content_ocr_raw = load_json(os.path.join(directory, OCR_OUTPUT_FILE_NAME), None)

    if LLM_USE_OCR:
        content_ocr_parsed = ask(prompt_ocr_parse.replace("{input}", content_ocr_raw), False)
        if content_ocr_parsed:
            content = f"{content_caption}\n\n{content_ocr_parsed}"
        else:
            content = content_caption
    else:
        content = content_caption

    evaluation = evaluate_content(prompt_value.replace("{input}", content))

    if evaluation == "true":
        result = parse_content(prompt_parse.replace("{input}", content))
    else:
        result = []

    write_json(os.path.join(directory, LLM_OUTPUT_FILE_NAME), result)

    print(
        f"Result for {post.media_id}: Evaluation: {evaluation} and Parse: {'Failed' if result is not [] else 'Success'} and Result: {result}")


if __name__ == "__main__":
    main()


def load_ai_prompt(file_path):
    return load_file(file_path).replace("{year}", f"{datetime.datetime.now().year}")
