import datetime
import os

import icalendar
from caldav.davclient import DAVClient

from tracker import use_tracker, PostTracker
from util.config import LLM_OUTPUT_FILE_NAME, CALDAV_CALENDAR, CALDAV_USERNAME, CALDAV_PASSWORD, CALDAV_URL, \
    DESCRIPTION_FOOTER, USE_IMGINN_LINK
from util.use_json import use_json


def main():
    with use_tracker() as sync_tracker:
        caldav = DAVClient(
            url=CALDAV_URL,
            username=CALDAV_USERNAME,
            password=CALDAV_PASSWORD,
        )

        principal = caldav.principal()
        calendar = principal.calendar(CALDAV_CALENDAR)

        counter = 0
        duplicates_skipped = 0

        for post in sync_tracker.posts.values():
            if post.interpreted and not post.caldav_pushed:
                _counter, _duplicates_skipped = push_events(calendar, post)
                post.caldav_pushed = True
                counter += _counter
                duplicates_skipped += _duplicates_skipped

        print(f"Pushed {counter} events! Skipped {duplicates_skipped} duplicates!")


def push_events(calendar, post: PostTracker):
    counter = 0
    duplicates_skipped = 0
    with use_json(os.path.join(post.directory(), LLM_OUTPUT_FILE_NAME)) as json:
        for event_json in json["events"]:
            if 'duplicate' in event_json and event_json['duplicate']:
                duplicates_skipped += 1
            else:
                description_array = [event_json["description"]]
                if DESCRIPTION_FOOTER is not None:
                    description_array.append(DESCRIPTION_FOOTER.replace(
                        "{post_link}",
                        f"https://instagram.com/p/{post.shortcode}" if not USE_IMGINN_LINK else f"https://imginn.com/p/{post.shortcode}").replace(
                        "{post_shortcode}", post.shortcode))
                if event_json["link"] is not None:
                    description_array.append(event_json["link"])

                event = icalendar.Event()
                event.add("summary", event_json["title"])
                event.add("description", "\n\n".join(description_array))
                event.add("url", event_json["link"])
                event.add("location", location(event_json["location"]))

                start_datetime = datetime.datetime.fromisoformat(event_json["start_datetime"])
                end_datetime = datetime.datetime.fromisoformat(event_json["end_datetime"])

                if start_datetime.time() == datetime.time(0, 0, 0):
                    event.add("dtstart", start_datetime.date())
                else:
                    event.add("dtstart", start_datetime)

                if end_datetime.time() == datetime.time(23, 59, 59):
                    event.add("dtend", end_datetime.date())
                else:
                    event.add("dtend", end_datetime)

                calendar.add_event(event.to_ical())
                counter += 1
    return counter, duplicates_skipped


def location(location_json):
    type = location_json["type"]
    offline_address = location_json["offline_address"]
    online_link = location_json["online_link"]
    if type == "Unknown" or type == "International" or type == "Bundesweit":
        return type
    elif type == "Online":
        return online_link if online_link else "Unknown"
    elif type == "Offline":
        return offline_address if offline_address else "Unknown"
    elif type == "Hybrid":
        return f"Hybrid: {offline_address} | {online_link}"


if __name__ == "__main__":
    main()
