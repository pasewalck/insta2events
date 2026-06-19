import datetime
import os

from tracker import use_tracker
from util.config import LLM_OUTPUT_FILE_NAME
from util.ollama_client import compare_duplicate
from util.use_json import use_json


def main():
    datetime_map = {}

    with (use_tracker() as sync_tracker):
        targets = sync_tracker.posts.values()
        targets_sorted = sorted(targets, key=lambda target: target.likes if target.likes is not None else 0,
                                reverse=True)
        for post in targets_sorted:
            if post.interpreted:
                with use_json(os.path.join(post.directory(), LLM_OUTPUT_FILE_NAME)) as json:
                    if "events" in json:
                        for event_json in json["events"]:
                            key_datetime = datetime.datetime.fromisoformat(event_json['start_datetime']).date()

                            if key_datetime not in datetime_map.keys():
                                datetime_map[key_datetime] = []
                                datetime_map[key_datetime].append(event_json)
                                event_json['duplicate'] = False

                                if "duplicate" in event_json:

                                    if not event_json['duplicate']:
                                        for compare_event_json in datetime_map[key_datetime]:
                                            if compare_duplicate(event_json, compare_event_json):
                                                print(
                                                    f"Marking Duplicate (LLM Matching): {event_json['title']}")
                                                event_json['duplicate'] = True
                                                break
                                        if not event_json['duplicate']:
                                            datetime_map[key_datetime].append(event_json)
                                    else:
                                        event_json['duplicate'] = False


if __name__ == "__main__":
    main()
