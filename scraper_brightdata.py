import os
from datetime import datetime, timedelta

import requests

from tracker import SocialMediaTracker, PostTracker, use_tracker, AccountDetails
from util.brightdata_service import request_with_cache
from util.config import (
    SCRAPE_ACCOUNTS,
    SYNC_SINCE,
    DOWNLOAD_PHOTOS,
    BRIGHTDATA_API_KEY,
)

account_usernames = (
    [u.strip() for u in SCRAPE_ACCOUNTS.split(",") if u.strip()]
    if SCRAPE_ACCOUNTS
    else []
)

until = datetime.now()


def _download_image(image_url: str, dest_path: str) -> None:
    try:
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
    except Exception as e:
        print(f"  Warning: failed to download image {image_url}: {e}")


def _save_post_data(image_urls: list, caption: str, post_dir: str, download_photos: bool) -> None:
    os.makedirs(post_dir, exist_ok=True)
    caption = caption
    with open(os.path.join(post_dir, "data.txt"), "w", encoding="utf-8") as f:
        f.write(caption)

    if download_photos:
        for idx, image_url in enumerate(image_urls):
            if image_url:
                ext = ".jpg"
                image_path = os.path.join(post_dir, f"image_{idx}{ext}")
                if not os.path.exists(image_path):
                    print("  Downloading images ...")
                    _download_image(image_url, image_path)


def discover_profile(username: str) -> dict | None:
    print(f"Discovering profile for @{username} ...")
    dataset_id = "gd_l1vikfch901nx3by4"
    params = {
        "type": "discover_new",
        "discover_by": "user_name",
        "include_errors": "true",
    }
    body = {"input": [{"user_name": username}]}

    results = request_with_cache(dataset_id, params, body)

    if not results:
        print(f"  No profile data returned for @{username}")
        return None

    return results[0]


def discover_posts(username: str, since: datetime, end: datetime) -> list[dict]:
    profile_url = f"https://www.instagram.com/{username}"
    start_date_str = since.strftime("%m-%d-%Y")
    end_date_str = end.strftime("%m-%d-%Y")

    print(
        f"Discovering posts for @{username} from {start_date_str} to {end_date_str} ..."
    )
    dataset_id = "gd_lk5ns7kz21pck8jpis"
    params = {
        "type": "discover_new",
        "discover_by": "url",
        "include_errors": "true",
    }
    body = {
        "input": [
            {
                "url": profile_url,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "post_type": "Post",
            }
        ]
    }

    results = request_with_cache(dataset_id, params, body)

    if not results:
        print(f"  No post data returned for @{username}")
        return []

    return results


def download_account(username: str, sync_tracker: SocialMediaTracker):
    # 1. Discover profile info
    profile_data = discover_profile(username)
    if profile_data is None:
        print(f"Skipping @{username}: could not discover profile")
        return

    user_id = profile_data.get("id")
    identifier = f"profile.{user_id}"

    account_details = AccountDetails(
        name=profile_data.get("profile_name") or username,
        userid=user_id,
        bio=profile_data.get("biography") or "",
        links=profile_data.get("external_url"),
    )

    # 2. Determine sync window
    sync_tracker.sync_states[identifier] = datetime.fromisoformat("2026-03-13")

    sync_state = sync_tracker.sync_states.get(
        identifier, datetime.fromisoformat(SYNC_SINCE)
    )

    print((until - sync_state))
    if (until - sync_state) < timedelta(hours=24):
        print(
            f"Not Scraping for {identifier} since latest sync state: {sync_state.strftime('%Y-%m-%d %H:%M:%S')}. Last sync too recent."
        )
        return

    print(
        f"Scraping for {identifier} since latest sync state: {sync_state.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # 3. Discover post URLs in time range
    posts = discover_posts(username, since=sync_state, end=until)
    if not posts:
        print(f"  No posts found for @{username}")
        sync_tracker.sync_states[identifier] = until
        return

    # 5. Process each post
    posts_count = 0
    for post in posts:
        post_id = post.get("post_id")

        if not post_id:
            continue

        user_posted = post.get("user_posted")
        if user_posted != username:
            continue

        post_url = post.get("url", "")
        shortcode = (
            post_url.rstrip("/").split("/")[-1] if "/p/" in post_url else post_id
        )

        post_date_str = post.get("date_posted")
        if post_date_str:
            post_date = datetime.fromisoformat(
                post_date_str.replace("Z", "+00:00")
            ).replace(tzinfo=None)
        else:
            post_date = datetime.now()

        likes = post.get("likes") or 0

        # Save post data to disk
        sync_tracker.posts[post_id] = PostTracker(
            media_id=post_id,
            shortcode=shortcode,
            likes=likes,
            date=post_date,
            photos_downloaded=DOWNLOAD_PHOTOS,
            source=identifier,
            account_details=account_details,
        )
        _save_post_data(post.get("photos", [post.get("thumbnail")]), post.get("description") or "",
                        sync_tracker.posts[post_id].directory(),
                        DOWNLOAD_PHOTOS)

        posts_count += 1
        print(
            f"  {posts_count}/{len(posts)}: https://www.instagram.com/p/{shortcode}"
        )

    sync_tracker.sync_states[identifier] = until
    print(f"Scraped {posts_count} posts for {identifier}")


def main():
    if not BRIGHTDATA_API_KEY:
        print("Error: BRIGHTDATA_API_KEY is not set. Add it to your .env file.")
        return

    with use_tracker() as sync_tracker:
        print(f"Scraping everything since latest sync states!")

        for account_username in account_usernames:
            download_account(account_username, sync_tracker)

        print(
            f"All new content was scraped. Updating sync state to: {until.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        sync_tracker.sync_state = until


if __name__ == "__main__":
    main()
