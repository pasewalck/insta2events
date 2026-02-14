import time
from datetime import datetime
from itertools import dropwhile, takewhile
from random import Random

import instaloader
from instaloader import Instaloader, Profile, QueryReturnedNotFoundException, Hashtag
from numpy.f2py.auxfuncs import throw_error

from tracker import SocialMediaTracker, PostTracker, use_tracker, AccountDetails
from util.config import DATA_PARENT_FOLDER, LOGIN_SESSION_FILE, LOGIN_USERNAME, SCRAPE_ACCOUNTS, SCRAPE_HASHTAGS, \
    POSTS_FOLDER_NAME, SYNC_SINCE, DOWNLOAD_PHOTOS

account_usernames = SCRAPE_ACCOUNTS.split(",") if SCRAPE_ACCOUNTS != "" else []
hashtags = SCRAPE_HASHTAGS.split(",") if SCRAPE_ACCOUNTS != "" else []

until = datetime.now()
random = Random()


def download(instaloader_instance: Instaloader, mode, target_username_or_hashtag: str,
             sync_tracker: SocialMediaTracker):
    if mode is not Profile and mode is not Hashtag:
        throw_error("Mode is Invalid!")
        return
    try:
        if mode is Profile:
            item = instaloader.Profile.from_username(instaloader_instance.context, target_username_or_hashtag)
        else:
            item = instaloader.Hashtag.from_name(instaloader_instance.context, target_username_or_hashtag)
    except QueryReturnedNotFoundException:
        return

    identifier = f"profile.{item.userid}" if mode is Profile else f"hashtag.{item.name}"
    posts = item.get_posts() if mode is Profile else item.get_posts_resumable()
    sync_state = sync_tracker.sync_states.get(identifier, datetime.fromisoformat(SYNC_SINCE))

    print(f"Scraping for {identifier} since latest sync state: {sync_state.strftime('%Y-%m-%d %H:%M:%S')}")

    posts_to_download = takewhile(lambda p: p.date > sync_state, dropwhile(lambda p: p.date > until, posts))
    posts_count = 0

    _posts_to_download = []

    posts_total_count = 0
    for post in posts_to_download:
        posts_total_count += 1
        _posts_to_download.append(post)

    for post in _posts_to_download:
        instaloader_instance.download_post(post, post.mediaid)
        account_details = AccountDetails(
            post.owner_profile.username,
            post.owner_profile.userid,
            post.owner_profile.biography,
            post.owner_profile.external_url
        )

        if post.mediaid in sync_tracker.posts:
            sync_tracker.posts[post.mediaid].sources.append(identifier)
        else:
            print(post.owner_profile.external_url)
            sync_tracker.posts[post.mediaid] = PostTracker(post.mediaid, post.shortcode, post.likes, post.date,
                                                           DOWNLOAD_PHOTOS,
                                                           identifier,
                                                           account_details)

        posts_count += 1
        print(f"{posts_count}/{posts_total_count}: https://imginn.com/p/{post.shortcode}")

    sync_tracker.sync_states[identifier] = until
    print(f"Scraped {posts_count} for {identifier}")

    time.sleep(random.randint(1, 2))


def main():
    l = instaloader.Instaloader(dirname_pattern=f"{DATA_PARENT_FOLDER}/{POSTS_FOLDER_NAME}/{{mediaid}}",
                                filename_pattern=DATA_PARENT_FOLDER, download_videos=False,
                                download_pictures=DOWNLOAD_PHOTOS)
    if LOGIN_USERNAME is not None and LOGIN_SESSION_FILE is not None:
        l.load_session_from_file(LOGIN_USERNAME, LOGIN_SESSION_FILE)
        print("Instaloader initialized with login")
    else:
        print("Instaloader initialized without login")

    with use_tracker() as sync_tracker:

        print(f"Scraping everything since latest sync states!")

        for hashtag in hashtags:
            if hashtag != "":
                download(l, instaloader.Hashtag, hashtag, sync_tracker)
        for account_username in account_usernames:
            if account_username != "":
                download(l, instaloader.Profile, account_username, sync_tracker)

        print(f"All new content was scraped. Updating sync state to: {until.strftime('%Y-%m-%d %H:%M:%S')}")

        sync_tracker.sync_state = until


if __name__ == "__main__":
    main()
