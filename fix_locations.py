import json
import os

from tracker import use_tracker
from util.config import LLM_OUTPUT_FILE_NAME
from util.nominatim import Nominatim
from util.ollama_client import llm_fix_location
from util.use_json import use_json


def sort_posts_by_likes(posts):
    return sorted(
        posts,
        key=lambda post: post.likes or 0,
        reverse=True
    )


def validate_or_fix_location(event):
    location = event.get("location", {})
    if location.get("type") != "Offline":
        return

    title = event.get("title", "Unknown Event")
    offline_address = location.get("offline_address")

    nominatim = Nominatim()
    current_result = nominatim.get_location_full_name(offline_address) if offline_address else None

    if current_result:
        print(f"Found valid location for {title} with {current_result}")
        location["overwritten_offline_address"] = offline_address
        location["offline_address"] = current_result
        return

    result = llm_fix_location(json.dumps(event))
    if result:
        print(f"Set validated location for {title} with {result}")
        location["overwritten_offline_address"] = offline_address
        location["offline_address"] = result
    else:
        print(f"Failed to fix location for {title}")


def process_post(post):
    if not post.interpreted:
        return

    json_path = os.path.join(post.directory(), LLM_OUTPUT_FILE_NAME)

    with use_json(json_path) as json_data:
        events = json_data.get("events", [])
        for event in events:
            if not event.get("ran_location_validation", False):
                validate_or_fix_location(event)
                event["ran_location_validation"] = True


def main():
    with use_tracker() as sync_tracker:
        posts = sync_tracker.posts.values()
        sorted_posts = sort_posts_by_likes(posts)

        for post in sorted_posts:
            process_post(post)


if __name__ == "__main__":
    main()
