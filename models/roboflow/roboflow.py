from roboflow import Roboflow
import os

from dotenv import load_dotenv
load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW = {
    "hauwei": {
        "project": "gui-detection-elc31",
        "version": 3,
    },
    "hallym": {
        "project": "hasdkfjhalkvuasdhafjlkasdhfheui",
        "version": 1,
    },
}


def get_processed_predictions(model, image_path, overlap_threshold=0.5):
    overlap_threshold *= 100

    pred = model.predict(
        image_path, confidence=0, overlap=overlap_threshold).json()
    
    # Add the image_path to the image attribute
    image_path = pred['predictions'][0]['image_path']
    pred['image']['path'] = image_path

    # Extract the game folder and name from the image_path
    game_folder, image_name = os.path.split(image_path)
    game_name = os.path.basename(game_folder)
    base_name = os.path.splitext(image_name)[0]

    pred['title'] = f"{game_name}_{base_name}"

    for prediction in pred['predictions']:
        # Remove the detection_id, image_path, and prediction_type
        del prediction['detection_id']
        del prediction['image_path']
        del prediction['prediction_type']

        # Calculate the center point of the detection box
        top_left_x = prediction['x'] - prediction["width"] // 2
        top_left_y = prediction["y"] - prediction["height"] // 2

        # Add the center point to the prediction
        prediction['top_left'] = (top_left_x, top_left_y)

    return pred

def get_roboflow_predictions(model_name, image_path, overlap_threshold=0.5):
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace().project(ROBOFLOW[model_name]["project"])
    model = project.version(ROBOFLOW[model_name]["version"]).model

    return get_processed_predictions(model, image_path, overlap_threshold)
