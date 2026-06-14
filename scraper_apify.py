import os
from datetime import datetime
from random import Random

import requests
from requests import HTTPError
from retry import retry

from tracker import SocialMediaTracker, use_tracker, PostTracker, AccountDetails
from util import config
from util.apify.apify import get_posts, get_profiles
from util.config import SCRAPE_ACCOUNTS, SCRAPE_HASHTAGS, DOWNLOAD_PHOTOS

account_usernames = SCRAPE_ACCOUNTS.split(",") if SCRAPE_ACCOUNTS != "" else []
hashtags = SCRAPE_HASHTAGS.split(",") if SCRAPE_ACCOUNTS != "" else []

now = datetime.now()
until = datetime(now.year, now.month, now.day, 0, 0, 0)
random = Random()


def download(usernames: list[str], sync_tracker: SocialMediaTracker):
    sync_since = (
        sync_tracker.last_sync
        if hasattr(sync_tracker, "last_sync") and sync_tracker.last_sync
        else datetime.fromisoformat(config.SYNC_SINCE)
    )
    posts = get_posts(usernames, sync_since)
    owner_usernames = set()
    for post in posts:
        owner_usernames.add(post.ownerUsername)

    profiles = get_profiles(list(owner_usernames))

    profile_map = {}
    account_detail_map = {}
    for profile in profiles:
        profile_map[profile.username] = profile
        account_detail_map[profile.username] = AccountDetails(
            name=profile.fullName,
            userid=profile.id,
            bio=profile.biography,
            links=profile.externalUrls,
        )

    for idx, post in enumerate(posts):
        if sync_tracker.posts.get(post.id) is not None:
            print(f"Skipping Post {idx}/{len(posts)}")
            continue

        print(f"Saving Post {idx}/{len(posts)}")

        sync_tracker.posts[post.id] = PostTracker(
            media_id=post.id,
            shortcode=post.shortCode,
            likes=post.likesCount,
            date=post.timestamp,
            photos_downloaded=DOWNLOAD_PHOTOS,
            account_details=account_detail_map[post.ownerUsername],
        )
        _save_post_data(post.images if len(post.images) > 0 else [post.displayUrl], post.caption,
                        sync_tracker.posts[post.id].directory(),
                        DOWNLOAD_PHOTOS)


def _save_post_data(image_urls: list, caption: str, post_dir: str, download_photos: bool) -> None:
    os.makedirs(post_dir, exist_ok=True)
    with open(os.path.join(post_dir, "data.txt"), "w", encoding="utf-8") as f:
        f.write(caption)

    if download_photos:
        for idx, image_url in enumerate(image_urls):
            if image_url:
                ext = ".jpg"
                image_path = os.path.join(post_dir, f"image_{idx}{ext}")
                if not os.path.exists(image_path):
                    print(f"  [{idx}/{len(image_urls)}] Downloading images ...")
                    _download_image(image_url, image_path)


@retry(HTTPError, tries=3, delay=2)
def _download_image(image_url: str, dest_path: str) -> None:
    try:
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
    except Exception as e:
        print(f"  Warning: failed to download image {image_url}: {e}")


def main():
    with use_tracker() as sync_tracker:
        print(f"Scraping everything since latest sync states!")

        download(account_usernames, sync_tracker)

        print(
            f"All new content was scraped. Updating sync state to: {until.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        sync_tracker.last_sync = until


if __name__ == "__main__":
    main()
