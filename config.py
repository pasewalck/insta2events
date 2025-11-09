import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

DATA_PARENT_FOLDER = os.getenv("PARENT_FOLDER", "data")
POSTS_FOLDER_NAME = os.getenv("PARENT_FOLDER", "posts")
SYNC_FILE_NAME = os.getenv("SYNC_FILE_NAME", "sync.pkl")
OCR_OUTPUT_FILE_NAME = os.getenv("SYNC_FILE_NAME", "ocr_output.json")
LLM_OUTPUT_FILE_NAME = os.getenv("SYNC_FILE_NAME", "result_llm.json")
PROMPT_OCR_PARSE_FILE = os.getenv("PROMPT_OCR_PARSE_FILE", "prompts/de/prompt-ocr-parse.txt")
PROMPT_VALUE_FILE = os.getenv("PROMPT_VALUE_FILE", "prompts/de/prompt-value.txt")
PROMPT_PARSE_FILE = os.getenv("PROMPT_PARSE_FILE", "prompts/de/prompt-parse.txt")
MODEL_SMALL = os.getenv("MODEL_SMALL", "qwen2.5:3b")
MODEL_LARGE = os.getenv("MODEL_LARGE", "qwen2.5")
LLM_USE_OCR = os.getenv("LLM_USE_OCR", False)
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_SESSION_FILE = os.getenv("LOGIN_SESSION_FILE")
SCRAPE_ACCOUNTS = os.getenv("SCRAPE_ACCOUNTS", "")
SCRAPE_HASHTAGS = os.getenv("SCRAPE_HASHTAGS", "")
SYNC_SINCE = os.getenv("SYNC_SINCE", datetime(2025, 1, 1).isoformat())
