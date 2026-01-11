import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

DATA_PARENT_FOLDER = os.getenv("PARENT_FOLDER", "./data")
POSTS_FOLDER_NAME = os.getenv("PARENT_FOLDER", "posts")
SYNC_FILE_NAME = os.getenv("SYNC_FILE_NAME", "sync.pkl")
OCR_OUTPUT_FILE_NAME = os.getenv("OCR_OUTPUT_FILE_NAME", "ocr_output.json")
LLM_OUTPUT_FILE_NAME = os.getenv("LLM_OUTPUT_FILE_NAME", "result_llm.json")
PROMPT_VALUE_FILE = os.getenv("PROMPT_VALUE_FILE", "./prompts/en/prompt-value.txt")
PROMPT_PARSE_VISION_FILE = os.getenv("PROMPT_VALUE_FILE", "./prompts/en/prompt-parse-vision.txt")
PROMPT_PARSE_FILE = os.getenv("PROMPT_PARSE_FILE", "./prompts/en/prompt-parse.txt")
LLM_PASS_IMAGES_DIRECTLY = os.getenv("LLM_PASS_IMAGES_DIRECTLY", False)
MODEL_SMALL = os.getenv("MODEL_SMALL", "gemma3:4b")
MODEL_LARGE = os.getenv("MODEL_LARGE", "deepseek-r1:8b")
MODEL_VISION = os.getenv("MODEL_VISION", "llama3.2-vision")
INTERPRETER_USE_OCR = os.getenv("INTERPRETER_USE_OCR", False)
DOWNLOAD_PHOTOS = os.getenv("DOWNLOAD_PHOTOS", True)
CLASSIFIER_USE_OCR = os.getenv("CLASSIFIER_USE_OCR", False)
INTERPRETER_CLASSIFIER_MODE = os.getenv("INTERPRETER_CLASSIFIER_MODE", "basic")
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_SESSION_FILE = os.getenv("LOGIN_SESSION_FILE")
SCRAPE_ACCOUNTS = os.getenv("SCRAPE_ACCOUNTS", "")
SCRAPE_HASHTAGS = os.getenv("SCRAPE_HASHTAGS", "")
RERUN_INTERPRETER = os.getenv("RERUN_INTERPRETER", False)
RERUN_CLASSIFIER = os.getenv("RERUN_CLASSIFIER", False)
OCR_ONLY_ON_AS_EVENT_CLASSIFIED = os.getenv("OCR_ONLY_ON_AS_EVENT_CLASSIFIED", True)
SYNC_SINCE = os.getenv("SYNC_SINCE", datetime(2025, 12, 1).isoformat())
