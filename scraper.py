from datetime import datetime
from itertools import dropwhile, takewhile

import instaloader
from instaloader import Instaloader, Hashtag, Profile, QueryReturnedNotFoundException

from config import DATA_PARENT_FOLDER, LOGIN_SESSION_FILE, LOGIN_USERNAME, SCRAPE_ACCOUNTS, SCRAPE_HASHTAGS, \
    POSTS_FOLDER_NAME, SYNC_SINCE
from tracker import SocialMediaTracker, PostTracker, use_tracker, AccountDetails

account_usernames = SCRAPE_ACCOUNTS.split(",") if SCRAPE_ACCOUNTS != "" else []
hashtags = SCRAPE_HASHTAGS.split(",") if SCRAPE_ACCOUNTS != "" else []

until = datetime.now()


def download(l: Instaloader, mode, target, sync_tracker: SocialMediaTracker):
    try:
        obj = instaloader.Profile.from_username(l.context,
                                                target) if mode == Profile else instaloader.Hashtag.from_name(
            l.context, target)
    except QueryReturnedNotFoundException:
        return

    identifier = obj.userid if mode is Profile else (f"#{obj.name}" if mode is Hashtag else None)
    posts = obj.get_posts() if mode is Profile else obj.get_posts_resumable()
    sync_state = sync_tracker.sync_states[
        identifier] if sync_tracker.sync_states.get(identifier) is not None else datetime.fromisoformat(
        SYNC_SINCE)
    print(f"Scraping for {identifier} since latest sync state: {sync_state.strftime('%Y-%m-%d %H:%M:%S')}")
    posts = takewhile(lambda p: p.date > sync_state, dropwhile(lambda p: p.date > until, posts))
    i_tracker = 0
    for post in posts:
        l.download_post(post, post.mediaid)
        if sync_tracker.posts.get(post.mediaid) is not None:
            sync_tracker.posts[post.mediaid].sources.append(identifier)
        else:
            owner_profile = post.owner_profile
            account_details = AccountDetails(owner_profile.username, owner_profile.userid, owner_profile.biography,
                                             owner_profile.external_url)
            print(owner_profile.external_url)
            sync_tracker.posts[post.mediaid] = (PostTracker(post.mediaid, post.date, True, identifier, account_details))
        i_tracker += 1
        print(f"{i_tracker}/?")
    sync_tracker.sync_states[identifier] = until
    print(f"Scraped {i_tracker} for {identifier}")


def main():
    l = instaloader.Instaloader(dirname_pattern=f"{DATA_PARENT_FOLDER}/{POSTS_FOLDER_NAME}/{{mediaid}}",
                                filename_pattern=DATA_PARENT_FOLDER, download_videos=False)
    if LOGIN_USERNAME is not None and LOGIN_SESSION_FILE is not None:
        l.load_session_from_file(LOGIN_USERNAME, LOGIN_SESSION_FILE)
        print("Instaloader initialized with login")
    else:
        print("Instaloader initialized without login")

    with use_tracker() as sync_tracker:

        print(f"Scraping everything since latest sync states!")

        for hashtag in hashtags:
            download(l, instaloader.Hashtag, hashtag, sync_tracker)
        for account_username in account_usernames:
            download(l, instaloader.Profile, account_username, sync_tracker)

        print(f"All new content was scraped. Updating sync state to: {until.strftime('%Y-%m-%d %H:%M:%S')}")

        sync_tracker.sync_state = until


if __name__ == "__main__":
    main()
