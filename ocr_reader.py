import os

import cv2
import easyocr

from config import POSTS_FOLDER_NAME, DATA_PARENT_FOLDER, OCR_OUTPUT_FILE_NAME
from tracker import use_tracker, PostTracker
from util.files_operations import write_json


def run_ocr(post: PostTracker, reader: easyocr.Reader):
    directory = os.path.join(DATA_PARENT_FOLDER, POSTS_FOLDER_NAME, f"{post.media_id}")
    output = []

    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.webp')):
            image_path = os.path.join(directory, filename)

            try:
                image = cv2.imread(image_path)
                results = reader.readtext(image)
                final_text = group_adjacent_text(results)
                output.append(final_text)
            except FileNotFoundError:
                print("Error: The image file was not found.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    print(f"OCR Parsed in {post.media_id}: {output}")
    write_json(os.path.join(directory, OCR_OUTPUT_FILE_NAME), output)


def group_adjacent_text(results, threshold_x=10, threshold_y=10, filter_confidence=0.5):
    linked_text = []
    current_group = []
    current_group_bbox = []

    for (bbox, text, confidence) in results:
        x_start, y_start = bbox[0]
        x_end, y_end = bbox[2]
        y_size = y_end - y_start

    for (bbox, text, confidence) in results:

        if filter_confidence > confidence:
            continue

        if len(current_group) == 0:
            current_group.append(text)
            current_group_bbox.append(bbox)
            continue

        x_start, y_start = bbox[0]
        x_end, y_end = bbox[2]
        y_size = y_end - y_start

        last_bbox = current_group_bbox[len(current_group) - 1]
        last_x_start = last_bbox[0][0]
        last_x_end = last_bbox[2][0]
        last_y_start = last_bbox[0][1]
        last_y_end = last_bbox[2][1]
        last_y_size = last_y_end - last_y_start

        if last_x_end + threshold_x > x_start or last_y_end + threshold_y > y_start:
            current_group.append(text)
            current_group_bbox.append(bbox)
        else:
            linked_text.append(' '.join(current_group))
            current_group = [text]
            current_group_bbox = [bbox]

    if current_group:
        linked_text.append(' '.join(current_group))

    return linked_text


def main():
    reader = easyocr.Reader(['de'])

    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            if not post.ocr_ran:
                run_ocr(post, reader)
                post.ocr_ran = True


if __name__ == "__main__":
    main()
