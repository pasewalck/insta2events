import datetime
import os
from typing import ContextManager

from config import DATA_PARENT_FOLDER, SYNC_SINCE, SYNC_FILE_NAME
from util.use_pickel import use_pickel


class PostTracker:
    def __init__(self, media_id, date, photos_downloaded):
        self.media_id = media_id
        self.date = date
        self.photos_downloaded = photos_downloaded
        self.ocr_ran = False
        self.interpreted = False


class SocialMediaTracker:
    def __init__(self, sync_start_state=None):
        self.posts = []
        self.sync_start_state = sync_start_state
        self.sync_state = sync_start_state


def use_tracker() -> ContextManager[SocialMediaTracker]:
    return use_pickel(os.path.join(DATA_PARENT_FOLDER, SYNC_FILE_NAME),
                      SocialMediaTracker(datetime.datetime.fromisoformat(SYNC_SINCE)))
