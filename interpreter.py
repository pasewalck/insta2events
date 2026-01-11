import os

from tracker import use_tracker, PostTracker
from util.config import LLM_OUTPUT_FILE_NAME, RERUN_INTERPRETER
from util.files_operations import write_json
from util.llm import llm_parse_events


def main():
    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            if (not post.interpreted or RERUN_INTERPRETER) and post.classified_as_event:
                run_interpreter(post)
                post.interpreted = True


def run_interpreter(post: PostTracker):
    result = llm_parse_events(post)
    print(f"Parsed: {result}" if result != "[]" else f"Parse failed!")
    write_json(os.path.join(post.directory(), LLM_OUTPUT_FILE_NAME), result)


if __name__ == "__main__":
    main()
