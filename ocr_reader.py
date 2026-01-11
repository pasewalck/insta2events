import os

import cv2
import easyocr
import numpy as np
import supervision as sv

from tracker import use_tracker, PostTracker
from util.config import OCR_OUTPUT_FILE_NAME, OCR_ONLY_ON_AS_EVENT_CLASSIFIED
from util.files_operations import write_json


def run_ocr(post: PostTracker, reader: easyocr.Reader):
    output_list = []
    for i, image_path in enumerate(post.get_image_paths(), start=1):
        try:
            image = cv2.imread(image_path)
            result = reader.readtext(image)
            output_list.append(simplify(result))
            if result is not []:
                save_debug_image(result, image, f"{post.media_id}-{i}")
        except FileNotFoundError:
            print("Error: The image file was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print(f"For {post.media_id} OCR Results: {output_list}")
    write_json(os.path.join(post.directory(), OCR_OUTPUT_FILE_NAME), output_list)


def save_debug_image(ocr_result, image, file_name):
    # Code from https://blog.roboflow.com/how-to-use-easyocr/
    xyxy, confidences, class_ids, label = [], [], [], []

    for detection in ocr_result:
        bbox, text, confidence = detection[0], detection[1], detection[2]
        length = len(text)

        x_min = int(min([point[0] for point in bbox]))
        y_min = int(min([point[1] for point in bbox]))
        x_max = int(max([point[0] for point in bbox]))
        y_max = int(max([point[1] for point in bbox]))

        xyxy.append([x_min, y_min, x_max, y_max])
        label.append(f"{text} Conf.: {confidence}")
        confidences.append(confidence)
        class_ids.append(0)

    detections = sv.Detections(
        xyxy=np.array(xyxy),
        confidence=np.array(confidences),
        class_id=np.array(class_ids)
    )

    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    annotated_image = box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=label)
    cv2.imwrite(os.path.join("./ocr", f"{file_name}.jpg"), annotated_image)


def simplify(raw_result):
    result = []

    for (bbox, text, confidence) in raw_result:
        result.append(text)

    return result


def main():
    reader = easyocr.Reader(['de', 'en'])

    with use_tracker() as sync_tracker:

        for post in sync_tracker.posts.values():
            if not post.ocr_ran and (not OCR_ONLY_ON_AS_EVENT_CLASSIFIED or post.classified_as_event):
                run_ocr(post, reader)
                post.ocr_ran = True


if __name__ == "__main__":
    main()
