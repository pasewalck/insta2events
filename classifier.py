import os
import re

from numpy.f2py.auxfuncs import throw_error

from config import PROMPT_VALUE_FILE, DATA_PARENT_FOLDER, \
    POSTS_FOLDER_NAME, OCR_OUTPUT_FILE_NAME, INTERPRETER_CLASSIFIER_MODE, \
    RERUN_CLASSIFIER, CLASSIFIER_USE_OCR
from llm import ask, load_ai_prompt
from tracker import use_tracker, PostTracker
from util.files_operations import load_file

# Load prompts
classifier_prompt = load_ai_prompt(PROMPT_VALUE_FILE)

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


def main():
    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            if not post.classified or RERUN_CLASSIFIER:
                post.classified_as_event = run_interpreter(post)
                print(f"Classification for {post.media_id}: {post.classified_as_event}")
                post.classified = True


def run_interpreter(post: PostTracker):
    directory = os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{post.media_id}")

    content_caption = load_file(os.path.join(directory, "data.txt"), None)
    content_ocr_raw = load_file(os.path.join(directory, OCR_OUTPUT_FILE_NAME), "None")
    use_ocr = CLASSIFIER_USE_OCR and content_ocr_raw is not None
    seems_to_be_event = classifier(content_caption) or (use_ocr and classifier(content_ocr_raw))
    return seems_to_be_event


def classifier(content):
    if INTERPRETER_CLASSIFIER_MODE == "basic":
        return classic_classifier(content)
    elif INTERPRETER_CLASSIFIER_MODE == "llm":
        return ai_classifier(content)
    else:
        throw_error("No Interpreter Mode")


def classic_classifier(text):
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


def ai_classifier(content):
    return ask(classifier_prompt.replace("{input}", content), False) == "true"


if __name__ == "__main__":
    main()
