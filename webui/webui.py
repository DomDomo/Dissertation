import os
import glob
import torch
from PIL import Image, ImageDraw
from torchvision import transforms
import json

PATH_TO_MODEL = "./model/screenrecognition-web350k-vins.torchscript"
PATH_TO_METADATA = "./metadata/class_map_vins_manual.json"


def load_model_and_metadata():
    model = torch.jit.load(PATH_TO_MODEL)

    with open(PATH_TO_METADATA, "r") as f:
        class_map = json.load(f)
    class_map = class_map['idx2Label']

    return model, class_map


def detect_ui_elements(model, class_map, image_path, confidence_threshold=0.4):
    # Load and transform the input image
    img_transforms = transforms.ToTensor()
    rgb_image = Image.open(image_path).convert('RGB')
    img_input = img_transforms(rgb_image)

    # Get predictions
    pred = model([img_input])[1]

    # Draw bounding boxes and labels
    draw = ImageDraw.Draw(rgb_image)
    print(len(pred[0]['boxes']))
    for i in range(len(pred[0]['boxes'])):
        conf_score = pred[0]['scores'][i]
        if conf_score > confidence_threshold:
            x1, y1, x2, y2 = pred[0]['boxes'][i]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            draw.rectangle([x1, y1, x2, y2], outline='red', width=4)
            label = class_map[str(int(pred[0]['labels'][i]))]
            draw.text((x1, y1), f"{label} {conf_score:.2f}", fill="red")

    return rgb_image


if __name__ == "__main__":
    model, class_map = load_model_and_metadata()

    image_paths = glob.glob('../idle_images/**/*.jpg', recursive=False)

    confidence_threshold = 0.2

    for image_path in image_paths[:3]:

        # Extract game and title from the image path
        game, title = image_path.split('\\')[1:]

        # Construct the prediction folder path
        prediction_folder = os.path.join(
            '../idle_images', game, 'webui_prediction', f"{confidence_threshold:.2f}")

        # Check if the prediction folder exists, create it if not
        if not os.path.exists(prediction_folder):
            os.makedirs(prediction_folder)

        # Make predictions (you've already implemented this)
        altered_image = detect_ui_elements(
            model, class_map, image_path, confidence_threshold)

        # Save the altered image with the new title and path
        new_title = f"{title.split('.')[0]}_{confidence_threshold:.2f}.jpg"
        new_image_path = os.path.join(prediction_folder, new_title)
        altered_image.save(new_image_path)

        print(
            f"Image '{title}' from '{game}' predicted and saved in '{prediction_folder}'")

    print("Done.")
