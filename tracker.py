import os
from typing import ContextManager

from util.config import DATA_PARENT_FOLDER, SYNC_FILE_NAME, POSTS_FOLDER_NAME
from util.files_operations import load_file
from util.use_pickel import use_pickel


class PostTracker:
    def __init__(self, media_id, shortcode, likes, date, photos_downloaded, source, account_details):
        self.media_id = media_id
        self.shortcode = shortcode
        self.date = date
        self.photos_downloaded = photos_downloaded
        self.interpreted = False
        self.likes = likes
        self.classified = False
        self.caldav_pushed = False
        self.classified_as_event = False
        self.interpretation_details: [InterpretationDetails] = []
        self.account_details: AccountDetails = account_details
        self.sources = [source]

    def directory(self):
        return os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{self.media_id}")

    def get_image_paths(self, limit=100):
        image_paths = []
        i = 0
        for filename in os.listdir(self.directory()):
            if filename.endswith(('.png', '.jpg', '.webp')) and i < limit:
                image_paths.append(os.path.join(self.directory(), filename))
                i += 1
        return image_paths

    def caption(self):
        return load_file(os.path.join(self.directory(), "data.txt"), None)


class InterpretationDetails:
    def __init__(self, name, start_date):
        self.name = name
        self.start_date = start_date


class AccountDetails:
    def __init__(self, name, userid, bio, link):
        self.name = name
        self.userid = userid
        self.bio = bio
        self.link = link


class SocialMediaTracker:
    def __init__(self, sync_start_state=None):
        self.posts = {}
        self.sync_states = {}


def use_tracker() -> ContextManager[SocialMediaTracker]:
    return use_pickel(os.path.join(DATA_PARENT_FOLDER, SYNC_FILE_NAME), SocialMediaTracker())
