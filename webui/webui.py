import os
import glob
import torch
from PIL import Image
from torchvision import transforms
import supervision as sv
import json
import cv2
import copy

PATH_TO_MODEL = "./model/screenrecognition-web350k-vins.torchscript"
PATH_TO_METADATA = "./metadata/class_map_vins_manual.json"


def load_model_and_metadata():
    model = torch.jit.load(PATH_TO_MODEL)

    with open(PATH_TO_METADATA, "r") as f:
        class_map = json.load(f)
    class_map = class_map['idx2Label']

    return model, class_map


def get_prediction_output(model, class_map, image_path):
    # Load and transform the input image
    img_transforms = transforms.ToTensor()
    rgb_image = Image.open(image_path).convert('RGB')
    img_input = img_transforms(rgb_image)


    # Extract the game folder and name from the image_path
    game_folder, image_name = os.path.split(image_path)
    game_name = os.path.basename(game_folder)
    base_name = os.path.splitext(image_name)[0]

    # Get predictions
    pred = model([img_input])[1]

    image_predictions = {
        "predictions": [
            {
                "x": int((x1 + x2) // 2),
                "y": int((y1 + y2) // 2),
                "width": int(x2 - x1),
                "height": int(y2 - y1),
                "confidence": pred[0]['scores'][i].item(),
                "class": class_map[str(int(pred[0]['labels'][i].item()))],
                "class_id": int(pred[0]['labels'][i].item()),
                "top_left": (int(x1), int(y1))
            }
            for i, (x1, y1, x2, y2) in enumerate([box.tolist() for box in pred[0]['boxes']])
        ],
        "image": {
            "width": rgb_image.size[0],
            "height": rgb_image.size[1],
            "path": image_path
        },
        "title": f"{game_name}_{base_name}"
    }

    return image_predictions

def display_pred_boxes(pred, image_path, confidence_threshold):
    pred_copy = copy.deepcopy(pred)

    pred_copy["predictions"] = \
        [p for p in pred_copy["predictions"] if p["confidence"] >= confidence_threshold]
    
    labels = [item["class"] for item in pred_copy["predictions"]]

    detections = sv.Detections.from_inference(pred_copy)
    
    label_annotator = sv.LabelAnnotator()
    bounding_box_annotator = sv.BoundingBoxAnnotator()

    image = cv2.imread(image_path)

    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    return annotated_image


if __name__ == "__main__":
    model, class_map = load_model_and_metadata()
    model_name = "huawei_prediction"

    image_paths = glob.glob('../idle_images/**/*.jpg', recursive=False)

    confidence_threshold = 0.2

    all_predictions = []

    for image_path in image_paths[:1]:

        # Extract game and title from the image path
        game, title = image_path.split('\\')[1:]

        # Construct the prediction folder path
        prediction_folder = os.path.join(
            '../idle_images', game, 'webui_prediction', f"{confidence_threshold:.2f}")

        # Check if the prediction folder exists, create it if not
        if not os.path.exists(prediction_folder):
            os.makedirs(prediction_folder)

        processed_predictions = get_prediction_output(model, class_map, image_path)
        all_predictions.append(processed_predictions)

        # Make predictions (you've already implemented this)
        altered_image = display_pred_boxes(processed_predictions, image_path, confidence_threshold)

        box_num = len(processed_predictions["predictions"])

        # Save the altered image with the new title and path
        new_title = f"{title.split('.')[0]}_{confidence_threshold:.2f}_{box_num}.jpg"
        new_image_path = os.path.join(prediction_folder, new_title)
        cv2.imwrite(new_image_path, altered_image)

        print(
            f"Image '{title}' from '{game}' predicted and saved in '{prediction_folder}'")
        
    with open(f"{model_name}s.json", 'w') as f:
        json.dump(all_predictions, f)

    print("Done.")
