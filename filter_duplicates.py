import datetime
import os

from tracker import use_tracker
from util.config import LLM_OUTPUT_FILE_NAME
from util.location import location
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
                            key_datetime = datetime.datetime.fromisoformat(event_json['start_datetime']).timestamp()
                            key = f"{key_datetime}{post.account_details.userid}"
                            event_json['duplicate'] = False

                            if key_datetime not in datetime_map.keys():
                                datetime_map[key_datetime] = []
                                datetime_map[key_datetime].append(event_json)
                            else:
                                is_duplicate = False
                                for compare_event_json in datetime_map[key_datetime]:
                                    title1 = compare_event_json['title'].lower().split()
                                    title2 = event_json['title'].lower().split()
                                    location1 = location(event_json["location"]).lower().split()
                                    location2 = location(event_json["location"]).lower().split()

                                    equal_word_count_title = sum(1 for word in title1 if word in title2)
                                    equal_word_count_ort = sum(1 for word in location1 if word in location2)

                                    if equal_word_count_title > len(title2) / 2 and equal_word_count_ort > len(
                                            title1) / 2:
                                        print(
                                            f"Marking Duplicate (Found via Date and Title and Ort Matching): {event_json['title']}  {key}")
                                        event_json['duplicate'] = True
                                        is_duplicate = True
                                        break
                                if not is_duplicate:
                                    datetime_map[key_datetime].append(event_json)


if __name__ == "__main__":
    main()
