import json
import os

from tracker import use_tracker, PostTracker
from util.config import DATA_PARENT_FOLDER, \
    INTERPRETER_USE_OCR, \
    PROMPT_PARSE_FILE, POSTS_FOLDER_NAME, OCR_OUTPUT_FILE_NAME, LLM_OUTPUT_FILE_NAME, RERUN_INTERPRETER, \
    OCR_OUTPUT_INTERPRETED_FILE_NAME
from util.files_operations import load_file, write_json
from util.llm import ask, load_ai_prompt

# Load prompts
prompt_parse = load_ai_prompt(PROMPT_PARSE_FILE)


def parse_content(content):
    return ask(content, True)


def main():
    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            if (not post.interpreted or RERUN_INTERPRETER) and post.classified_as_event:
                run_interpreter(post)
                post.interpreted = True


def run_interpreter(post: PostTracker):
    directory = os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{post.media_id}")

    content_caption = load_file(os.path.join(directory, "data.txt"), None)

    result = parse_content(
        prompt_parse.replace(
            "{input}", content_caption
        ).replace(
            "{input_ocr}",
            load_file(os.path.join(directory, OCR_OUTPUT_FILE_NAME), "No OCR Data.")
            if INTERPRETER_USE_OCR
            else "None"
        ).replace(
            "{owner_link}", post.account_details.link
        ).replace(
            "{owner_name}", post.account_details.name)
        .replace(
            "{owner_bio}", post.account_details.bio
        )
    )

    print(f"Parsed: {result}" if result != "[]" else f"Parse failed!")

    write_json(os.path.join(directory, LLM_OUTPUT_FILE_NAME), json.loads(result))


if __name__ == "__main__":
    main()
