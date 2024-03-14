from roboflow import Roboflow
import supervision as sv
import cv2
import glob
import os

from dotenv import load_dotenv
load_dotenv()

ROOT_IMAGE_FOLDER = "../idle_images"

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_PROJECT = "gui-detection-lygbf"
ROBOFLOW_PROJECT_VERSION = 1

MODEL_NAME = "huawei"


def detect_ui_elements(model, confidence_threshold, overlap_threshold, image_path):
    # Standardize to percentage
    confidence_threshold *= 100
    overlap_threshold *= 100

    pred = model.predict(
        image_path, confidence=confidence_threshold, overlap=overlap_threshold).json()

    labels = [item["class"] for item in pred["predictions"]]

    detections = sv.Detections.from_inference(pred)
    red = sv.Color(r=255, g=0, b=0)

    label_annotator = sv.LabelAnnotator(color=red)
    bounding_box_annotator = sv.BoxAnnotator(color=red)

    image = cv2.imread(image_path)

    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    return annotated_image


if __name__ == "__main__":
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace().project(ROBOFLOW_PROJECT)
    model = project.version(ROBOFLOW_PROJECT_VERSION).model
    model_name = "huawei_prediction"

    image_paths = glob.glob(f'{ROOT_IMAGE_FOLDER}/**/*.jpg', recursive=False)

    confidence_threshold = 0.2
    overlap_threshold = 0.5

    for image_path in image_paths[:1]:

        # Extract game and title from the image path
        game, title = image_path.split('\\')[1:]

        # Construct the prediction folder path
        prediction_folder = os.path.join(
            ROOT_IMAGE_FOLDER, game, f"{MODEL_NAME}_prediction", f"{confidence_threshold:.2f}")

        # Check if the prediction folder exists, create it if not
        if not os.path.exists(prediction_folder):
            os.makedirs(prediction_folder)

        # Make predictions (you've already implemented this)
        altered_image = detect_ui_elements(
            model, confidence_threshold, overlap_threshold, image_path)

        # Save the altered image with the new title and path
        new_title = f"{title.split('.')[0]}_{confidence_threshold:.2f}.jpg"
        new_image_path = os.path.join(prediction_folder, new_title)
        cv2.imwrite(new_image_path, altered_image)

        print(
            f"Image '{title}' from '{game}' predicted and saved in '{prediction_folder}'")

    print("Done.")
