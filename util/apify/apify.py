#!/usr/bin/env python3
import hashlib
import json
import os
import pickle
import time
from datetime import datetime
from typing import Any, List

import requests

from util import config
from util.apify.models import Profile, Post

# Cache directory
CACHE_DIR = os.path.join(config.DATA_PARENT_FOLDER, "apify_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _get_cache_key(actor_id: str, params: dict[str, Any]) -> str:
    """Generate a unique cache key based on actor_id and parameters."""
    params_str = json.dumps(params, sort_keys=True)
    hash_obj = hashlib.md5(params_str.encode())
    return f"{actor_id}_{hash_obj.hexdigest()}"


def _get_cache_path(cache_key: str) -> str:
    """Get the full path to a cache file."""
    return os.path.join(CACHE_DIR, f"{cache_key}.pkl")


def _load_from_cache(cache_key: str) -> Any | None:
    """Load data from cache file if it exists."""
    cache_path = _get_cache_path(cache_key)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except (pickle.PickleError, IOError):
            return None
    return None


def _save_to_cache(cache_key: str, data: Any) -> None:
    """Save data to cache file."""
    cache_path = _get_cache_path(cache_key)
    try:
        with open(cache_path, "wb") as f:
            pickle.dump(data, f)
    except (pickle.PickleError, IOError):
        pass  # Silently ignore cache write errors


def headers():
    return {"Content-Type": "application/json"}


def run_url(actor_id: str) -> str:
    return (
        f"https://api.apify.com/v2/acts/{actor_id}/runs?token={config.APIFY_API_TOKEN}"
    )


def run_status_url(run_id: str) -> str:
    return (
        f"https://api.apify.com/v2/actor-runs/{run_id}?token={config.APIFY_API_TOKEN}"
    )


def dataset_url(dataset_id: str) -> str:
    return f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={config.APIFY_API_TOKEN}"


def wait_for_run(run_id: str, timeout: int = 60 * 15) -> dict:
    url = run_status_url(run_id)
    start_time = time.time()
    index = 0
    while True:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        status = data.get("status")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED_OUT"):
            return data
        if time.time() - start_time > timeout:
            raise TimeoutError(
                f"Actor run {run_id} did not finish within {timeout} seconds"
            )
        time.sleep(min(16, 2 ** index))
        index += 1


def run(payload):
    actor_id = "shu8hvrXbJbY3Eb9W"
    # Check cache
    cache_key = _get_cache_key(actor_id, payload)
    cached_result = _load_from_cache(cache_key)

    if cached_result is not None:
        return cached_result

    resp = requests.post(
        run_url(actor_id),
        headers=headers(),
        data=json.dumps(payload),
        timeout=60,
    )
    resp.raise_for_status()

    data = resp.json().get("data", {})
    run_id = data.get("id")
    dataset_id = data.get("defaultDatasetId")

    wait_for_run(run_id)

    items_resp = requests.get(dataset_url(dataset_id), timeout=60)
    items_resp.raise_for_status()

    result = items_resp.json()
    _save_to_cache(cache_key, result)
    return result


def get_profiles(
        usernames: List[str],
) -> List[Profile]:
    usernames.sort()
    urls = [f"https://www.instagram.com/{username}" for username in usernames]
    payload = {
        "addParentData": False,
        "directUrls": urls,
        "resultsLimit": 1,
        "resultsType": "details",
        "searchLimit": 1,
        "searchType": "hashtag",
    }
    result = run(payload)
    return [Profile.from_dict(item) for item in result]


def get_posts(username_inputs: List[str], since: datetime) -> List[Post]:
    urls = [f"https://www.instagram.com/{username}" for username in username_inputs]
    payload: dict[str, Any] = {
        "directUrls": urls,
        "resultsType": "posts",
        "resultsLimit": 200,
        "onlyPostsNewerThan": since.isoformat().replace('+00:00', 'Z'),
        "searchLimit": 1,
        "addParentData": False,
        "searchType": "hashtag",
    }
    result = run(payload)
    return [Post.from_dict(item) for item in result]
