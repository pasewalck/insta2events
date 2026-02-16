import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

DATA_PARENT_FOLDER = os.getenv("PARENT_FOLDER", "./data")
POSTS_FOLDER_NAME = os.getenv("PARENT_FOLDER", "posts")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
SYNC_FILE_NAME = os.getenv("SYNC_FILE_NAME", "sync.pkl")
LLM_OUTPUT_FILE_NAME = os.getenv("LLM_OUTPUT_FILE_NAME", "result_llm.json")
LLM_PROMPT_OUTPUT_FILE_NAME = os.getenv("LLM_PROMPT_OUTPUT_FILE_NAME", "prompt_llm.txt")
PROMPT_CLASSIFY_FILE = os.getenv("PROMPT_VALUE_FILE", "./prompts/de/prompt-value.txt")
PROMPT_FIX_LOCATION_FILE = os.getenv("PROMPT_FIX_LOCATION_FILE", "./prompts/de/prompt-fix-location.txt")
WEB_SEARCH_ANALYSE_FILE = os.getenv("PROMPT_FIX_LOCATION_FILE", "./prompts/de/web-search-analyse.txt")
PROMPT_INTERPRETER_FILE = os.getenv("PROMPT_PARSE_FILE", "./prompts/de/prompt-parse.txt")
SEARCH_PLACE_TEMPLATE = "Adresse {place_name}"
LLM_PASS_IMAGES_DIRECTLY = os.getenv("LLM_PASS_IMAGES_DIRECTLY", "False") == "True"
MODEL_CLASSIFIER = os.getenv("MODEL_CLASSIFIER", "gemma3:4b")
MODEL_FIX_LOCATION = os.getenv("MODEL_FIX_LOCATION", "gemma3:4b")
MODEL_INTERPRETER = os.getenv("MODEL_INTERPRETER", "llama3.2-vision")
DOWNLOAD_PHOTOS = os.getenv("DOWNLOAD_PHOTOS", "True") == "True"
INTERPRETER_CLASSIFIER_MODE = os.getenv("INTERPRETER_CLASSIFIER_MODE", "basic")
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_SESSION_FILE = os.getenv("LOGIN_SESSION_FILE")
SCRAPE_ACCOUNTS = os.getenv("SCRAPE_ACCOUNTS", "")
SCRAPE_HASHTAGS = os.getenv("SCRAPE_HASHTAGS", "")
SAVE_PROMPT = os.getenv("SAVE_PROMPT", "False") == "True"
RERUN_INTERPRETER = os.getenv("RERUN_INTERPRETER", "False") == "True"
RERUN_CLASSIFIER = os.getenv("RERUN_CLASSIFIER", "False") == "True"
SYNC_SINCE = os.getenv("SYNC_SINCE", datetime(2026, 1, 1).isoformat())
USE_IMGINN_LINK = os.getenv("USE_IMGINN_LINK", "False") == "True"

CALDAV_URL = os.getenv("CALDAV_URL")
CALDAV_USERNAME = os.getenv("CALDAV_USERNAME")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")
CALDAV_CALENDAR = os.getenv("CALDAV_CALENDAR")
OLLAMA_KEY = os.getenv("OLLAMA_KEY")

DESCRIPTION_FOOTER = os.getenv("DESCRIPTION_FOOTER", "Sourced from Instagram Post: {post_link}")
