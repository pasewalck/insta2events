import datetime
import os

from tracker import use_tracker
from util.config import LLM_OUTPUT_FILE_NAME
from util.use_json import use_json


def main():
    date_owner_key_set = set()
    datetime_map = {}

    with (use_tracker() as sync_tracker):
        targets = sync_tracker.posts.values()
        targets_sorted = sorted(targets, key=lambda target: target.likes if target.likes is not None else 0,
                                reverse=True)
        for post in targets_sorted:
            if post.interpreted:
                with use_json(os.path.join(post.directory(), LLM_OUTPUT_FILE_NAME)) as json:
                    for event_json in json["events"]:
                        key_datetime = datetime.datetime.fromisoformat(event_json['start_datetime']).timestamp()
                        key = f"{key_datetime}{post.account_details.userid}"
                        if key in date_owner_key_set:
                            print(f"Marking Duplicate (Found via Date and Owner Matching): {event_json['title']} {key}")
                            event_json['duplicate'] = True
                        else:
                            if key_datetime not in datetime_map.keys():
                                datetime_map[key_datetime] = []
                                datetime_map[key_datetime].append(event_json)
                            else:
                                for compare_event_json in datetime_map[key_datetime]:
                                    words1 = compare_event_json['title'].lower().split()
                                    words2 = event_json['title'].lower().split()

                                    equal_word_count = sum(1 for word in words1 if word in words2)
                                    if equal_word_count > len(words2) / 2:
                                        print(
                                            f"Marking Duplicate (Found via Date and Title Matching): {event_json['title']} {key}")
                                        event_json['duplicate'] = True
                                    else:
                                        datetime_map[key_datetime].append(event_json)

                            date_owner_key_set.add(key)


if __name__ == "__main__":
    main()
