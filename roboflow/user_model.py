from roboflow import Roboflow
from inference_sdk import InferenceHTTPClient
import supervision as sv
import json
import cv2
import glob
import os

from dotenv import load_dotenv
load_dotenv()

ROOT_IMAGE_FOLDER = "../idle_images"

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
# ROBOFLOW_PROJECT = "hasdkfjhalkvuasdhafjlkasdhfheui"
# ROBOFLOW_PROJECT_VERSION = 1
# MODEL_NAME = "hallym"

ROBOFLOW_PROJECT = "gui-detection-elc31"
ROBOFLOW_PROJECT_VERSION = 3
MODEL_NAME = "hauwei"


def process_prediction_output(data):
    # Add the image_path to the image attribute
    image_path = data['predictions'][0]['image_path']
    data['image']['image_path'] = image_path

    # Extract the game folder and name from the image_path
    game_folder, image_name = os.path.split(image_path)
    game_name = os.path.basename(game_folder)
    base_name = os.path.splitext(image_name)[0]

    data['title'] = f"{game_name}_{base_name}"

    for prediction in data['predictions']:
        # Remove the detection_id, image_path, and prediction_type
        del prediction['detection_id']
        del prediction['image_path']
        del prediction['prediction_type']

        # Calculate the center point of the detection box
        top_left_x = prediction['x'] - prediction["width"] // 2
        top_left_y = prediction["y"] - prediction["height"] // 2

        # Add the center point to the prediction
        prediction['top_left'] = (top_left_x, top_left_y)

    return data


def detect_ui_elements(model, confidence_threshold, overlap_threshold, image_path):
    # Standardize to percentage
    confidence_threshold *= 100
    overlap_threshold *= 100

    pred = model.predict(
        image_path, confidence=0, overlap=overlap_threshold).json()
    

    labels = [item["class"] for item in pred["predictions"]]

    processed_data = process_prediction_output(pred)

    detections = sv.Detections.from_inference(pred)
    red = sv.Color(r=255, g=0, b=0)

    label_annotator = sv.LabelAnnotator(color=red)
    bounding_box_annotator = sv.BoxAnnotator(color=red)

    image = cv2.imread(image_path)

    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    return annotated_image, processed_data


if __name__ == "__main__":
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace().project(ROBOFLOW_PROJECT)
    model = project.version(ROBOFLOW_PROJECT_VERSION).model
    model_name = "huawei_prediction"

    image_paths = glob.glob(f'{ROOT_IMAGE_FOLDER}/**/*.jpg', recursive=False)

    confidence_threshold = 0.2
    overlap_threshold = 0.5

    all_predictions = []

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
        altered_image, processed_data = detect_ui_elements(
            model, confidence_threshold, overlap_threshold, image_path)
        
        box_num = len(processed_data["predictions"])

        # Save the altered image with the new title and path
        new_title = f"{title.split('.')[0]}_{confidence_threshold:.2f}_{box_num}.jpg"
        new_image_path = os.path.join(prediction_folder, new_title)
        cv2.imwrite(new_image_path, altered_image)


        # Save prediction data:
        all_predictions.append(processed_data)

        print(
            f"Image '{title}' from '{game}' predicted and saved in '{prediction_folder}'")
        
    with open(f"{model_name}s.json", 'w') as f:
        json.dump(all_predictions, f)

    print("Done.")
