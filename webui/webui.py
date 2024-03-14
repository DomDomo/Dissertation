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
    test_image = Image.open(image_path)
    img_input = img_transforms(test_image)

    # Get predictions
    pred = model([img_input])[1]

    # Draw bounding boxes and labels
    draw = ImageDraw.Draw(test_image)
    for i in range(len(pred[0]['boxes'])):
        conf_score = pred[0]['scores'][i]
        if conf_score > confidence_threshold:
            x1, y1, x2, y2 = pred[0]['boxes'][i]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            draw.rectangle([x1, y1, x2, y2], outline='red')
            label = class_map[str(int(pred[0]['labels'][i]))]
            draw.text((x1, y1), f"{label} {conf_score:.2f}", fill="red")

    return test_image


if __name__ == "__main__":
    model, class_map = load_model_and_metadata()

    # Call the function with your image path
    confidence_threshold = 0.5
    current_image = "main"

    current_image_path = f"./{current_image}.jpg"
    altered_image = detect_ui_elements(
        model, class_map, current_image_path, confidence_threshold)

    # Save the altered image
    output_path = f"./altered_{current_image}_{confidence_threshold}.jpg"
    altered_image.save(output_path)
