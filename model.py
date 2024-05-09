
import supervision as sv
import json
import cv2
import glob
import os
import copy


from models.roboflow.roboflow import get_roboflow_predictions
from models.webui.webui import get_webui_predictions

ROOT_IMAGE_FOLDER = "./idle_images"

HUAWEI_MODEL = "huawei"
HALLYM_MODEL = "hallym"
WEBUI_MODEL = "webui"


MODEL = WEBUI_MODEL  # Choose model here <--------


def get_model_results(model_name, image_path, overlap_threshold=0.5):
    if model_name == HUAWEI_MODEL or model_name == HALLYM_MODEL:
        return get_roboflow_predictions(model_name, image_path, overlap_threshold)
    elif model_name == WEBUI_MODEL:
        return get_webui_predictions(image_path)

    return -1


def display_pred_boxes(pred, confidence_threshold, image_path):
    pred_copy = copy.deepcopy(pred)

    print(pred_copy)

    pred_copy["predictions"] = \
        [p for p in pred_copy["predictions"]
            if p["confidence"] >= confidence_threshold]

    labels = [item["class"] for item in pred_copy["predictions"]]

    detections = sv.Detections.from_inference(pred_copy)

    red = sv.Color(r=255, g=0, b=0)
    label_annotator = sv.LabelAnnotator(color=red)
    bounding_box_annotator = sv.BoundingBoxAnnotator(color=red)

    image = cv2.imread(image_path)

    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    return annotated_image


if __name__ == "__main__":
    image_paths = glob.glob(f'{ROOT_IMAGE_FOLDER}/**/*.jpg', recursive=False)

    confidence_threshold = 0.45
    overlap_threshold = 0.5

    all_predictions = []
    for image_path in image_paths[:1]:
        # Extract game and title from the image path
        game, title = image_path.split('\\')[1:]

        # Construct the prediction folder path
        prediction_folder = os.path.join(
            ROOT_IMAGE_FOLDER, game, f"{MODEL}_prediction", f"{confidence_threshold:.2f}")

        # Check if the prediction folder exists, create it if not
        if not os.path.exists(prediction_folder):
            os.makedirs(prediction_folder)

        processed_predictions = get_model_results(MODEL, image_path)
        all_predictions.append(processed_predictions)

        altered_image = display_pred_boxes(
            processed_predictions, confidence_threshold, image_path)

        # Save the altered image with the new title and path
        new_title = f"{title.split('.')[0]}_{confidence_threshold:.2f}.jpg"
        new_image_path = os.path.join(prediction_folder, new_title)
        cv2.imwrite(new_image_path, altered_image)

        print(
            f"Image '{title}' from '{game}' predicted and saved in '{prediction_folder}'")

    with open(f"./predictions/{MODEL}/{MODEL}_predictions.json", 'w') as f:
        json.dump(all_predictions, f)

    print("Done.")
