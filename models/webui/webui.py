from torchvision import transforms
from PIL import Image
import torch
import json
import os


CURRENT_SCRIPT = os.path.dirname(os.path.realpath(__file__))
PATH_TO_MODEL = os.path.join(
    CURRENT_SCRIPT, "./weights/screenrecognition-web350k-vins.torchscript")
PATH_TO_METADATA = os.path.join(
    CURRENT_SCRIPT, "./metadata/class_map_vins_manual.json")


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
                "top_left": (int(x1), int(y1)),
                "bottom_right": (int(x2), int(y2))
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


def get_webui_predictions(image_path):
    model = torch.jit.load(PATH_TO_MODEL)

    with open(PATH_TO_METADATA, "r") as f:
        class_map = json.load(f)
    class_map = class_map['idx2Label']

    return get_prediction_output(model, class_map, image_path)
