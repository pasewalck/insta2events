from datetime import datetime
from itertools import dropwhile, takewhile

import instaloader
from instaloader import Instaloader

from config import DATA_PARENT_FOLDER, LOGIN_SESSION_FILE, LOGIN_USERNAME, SCRAPE_ACCOUNTS, SCRAPE_HASHTAGS, \
    POSTS_FOLDER_NAME
from tracker import SocialMediaTracker, PostTracker, use_tracker

account_usernames = SCRAPE_ACCOUNTS.split(",") if SCRAPE_ACCOUNTS != "" else []
hashtags = SCRAPE_HASHTAGS.split(",") if SCRAPE_ACCOUNTS != "" else []

until = datetime.now()


def download(l: Instaloader, posts, sync_tracker: SocialMediaTracker):
    posts = takewhile(lambda p: p.date > sync_tracker.sync_state, dropwhile(lambda p: p.date > until, posts))
    i_tracker = 0
    for post in posts:
        l.download_post(post, post.mediaid)
        sync_tracker.posts.append(PostTracker(post.mediaid, post.date, True))
        i_tracker += 1
    return i_tracker


def main():
    l = instaloader.Instaloader(dirname_pattern=f"{DATA_PARENT_FOLDER}/{POSTS_FOLDER_NAME}/{{mediaid}}",
                                filename_pattern=DATA_PARENT_FOLDER, download_videos=False)
    if LOGIN_USERNAME is not None and LOGIN_SESSION_FILE is not None:
        l.load_session_from_file(LOGIN_USERNAME, LOGIN_SESSION_FILE)
        print("Instaloader initialized with login")
    else:
        print("Instaloader initialized without login")

    with use_tracker() as sync_tracker:

        print(f"Scraping everything since latest sync state: {sync_tracker.sync_state.strftime('%Y-%m-%d %H:%M:%S')}")

        for hashtag in hashtags:
            print(f"Scraping for #{hashtag}")
            instaloader_hashtag = instaloader.Hashtag.from_name(l.context, hashtag)
            count = download(l, instaloader_hashtag.get_posts_resumable(), sync_tracker)
            print(f"Scraped {count} for #{hashtag}")

        for account_username in account_usernames:
            print(f"Scraping from @{account_username}")
            instaloader_profile = instaloader.Profile.from_username(l.context, account_username)
            count = download(l, instaloader_profile.get_posts(), sync_tracker)
            print(f"Scraped {count} for #{account_username}")

        print(f"All new content was scraped. Updating sync state to: {until.strftime('%Y-%m-%d %H:%M:%S')}")

        sync_tracker.sync_state = until


if __name__ == "__main__":
    main()
