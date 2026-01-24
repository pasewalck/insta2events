import os
from datetime import datetime

from tracker import use_tracker, PostTracker, InterpretationDetails
from util.config import LLM_OUTPUT_FILE_NAME, RERUN_INTERPRETER, LLM_PROMPT_OUTPUT_FILE_NAME
from util.files_operations import write_json, write_file
from util.ollama_client import llm_parse_events


def main():
    with use_tracker() as sync_tracker:
        targets = []
        for post in sync_tracker.posts.values():
            if (not post.interpreted or RERUN_INTERPRETER) and post.classified_as_event:
                targets.append(post)
        count = 0
        for post in targets:
            print(f"Post {count} / {len(targets)}")
            run_interpreter(post)
            post.interpreted = True
            count += 1


def run_interpreter(post: PostTracker):
    result, prompt = llm_parse_events(post)
    if result is not None:
        print(f"{len(result['events'])} events parsed!")
        write_json(os.path.join(post.directory(), LLM_OUTPUT_FILE_NAME), result)
        post.interpretation_details = []
        for event_json in result['events']:
            post.interpretation_details.append(InterpretationDetails(event_json["title"],
                                                                     datetime.fromisoformat(
                                                                         event_json["start_datetime"])))
    else:
        print("No event parsed!")
    write_file(os.path.join(post.directory(), LLM_PROMPT_OUTPUT_FILE_NAME), prompt)


if __name__ == "__main__":
    main()
