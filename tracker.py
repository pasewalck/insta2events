import os
from typing import ContextManager

from util.config import DATA_PARENT_FOLDER, SYNC_FILE_NAME, POSTS_FOLDER_NAME, OCR_OUTPUT_FILE_NAME
from util.files_operations import load_file
from util.use_pickel import use_pickel


class PostTracker:
    def __init__(self, media_id, date, photos_downloaded, source, account_details):
        self.media_id = media_id
        self.date = date
        self.photos_downloaded = photos_downloaded
        self.ocr_ran = False
        self.interpreted = False
        self.classified = False
        self.classified_as_event = False
        self.account_details: AccountDetails = account_details
        self.sources = [source]

    def directory(self):
        return os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{self.media_id}")

    def get_image_paths(self):
        image_paths = []
        for filename in os.listdir(self.directory()):
            if filename.endswith(('.png', '.jpg', '.webp')):
                image_paths.pop(os.path.join(self.directory(), filename))
        return image_paths

    def caption(self):
        return load_file(os.path.join(self.directory(), "data.txt"), None)

    def ocr_output(self):
        return load_file(os.path.join(self.directory(), OCR_OUTPUT_FILE_NAME), "None")


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
