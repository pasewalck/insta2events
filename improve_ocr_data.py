import json
import os

from tracker import use_tracker, PostTracker
from util.config import PROMPT_OCR_PARSE_FILE, DATA_PARENT_FOLDER, \
    POSTS_FOLDER_NAME, OCR_OUTPUT_FILE_NAME, OCR_OUTPUT_INTERPRETED_FILE_NAME
from util.files_operations import load_file, write_json
from util.llm import ask, load_ai_prompt

# Load prompts
prompt_ocr_improve = load_ai_prompt(PROMPT_OCR_PARSE_FILE)


def run_ocr_through_llm(ocr_raw, caption, post):
    return ask(prompt_ocr_improve.replace(
        "{input}", ocr_raw)
    .replace(
        "{caption}", caption)
    .replace(
        "{owner_link}", post.account_details.link
    ).replace(
        "{owner_name}", post.account_details.name)
    .replace(
        "{owner_bio}", post.account_details.bio
    ), False)


def main():
    with use_tracker() as sync_tracker:
        for post in sync_tracker.posts.values():
            if not post.ocr_improved:
                run_improver(post)
                post.ocr_improved = True


def run_improver(post: PostTracker):
    directory = os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{post.media_id}")
    content_ocr_raw = load_file(os.path.join(directory, OCR_OUTPUT_FILE_NAME), "None")
    content_caption = load_file(os.path.join(directory, "data.txt"), None)
    improved_ocr = run_ocr_through_llm(content_ocr_raw, content_caption, post)
    print(f"Improved OCR data from {post.media_id} to: {improved_ocr}")
    write_json(os.path.join(directory, OCR_OUTPUT_INTERPRETED_FILE_NAME), json.loads(improved_ocr))


if __name__ == "__main__":
    main()
