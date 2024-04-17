import supervision as sv
import json
import cv2
import json
import random

from models.webui.webui import get_webui_predictions


def draw_center_dots(image, pred):
    for prediction in pred["predictions"]:
        # Draw a red dot at the center point
        cv2.circle(image, (prediction["x"], prediction["y"]), radius=5, color=(
            255, 0, 0), thickness=-1)

    return image


def draw_dead_zones(image, box_coords, fix):
    overlay = image.copy()
    # The opacity level of the overlay, between 0 (completely transparent) and 1 (completely opaque)
    opacity = 0.5

    for box in box_coords:
        top_left = (box[0], box[1] - fix)
        bottom_right = (box[2], box[3] - fix)
        cv2.rectangle(overlay, top_left, bottom_right,
                      (0, 0, 255), -1)  # -1 fills the rectangle

    # Blend the original image with the overlay
    cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return image


def make_prediction_image(folder, filename, current, data, dead_zones, crop_fix):
    image_path = f"./{folder}/{filename}"

    labels = [str(round(p["confidence"], 5)) for p in data["predictions"]]
    detections = sv.Detections.from_inference(data)

    label_annotator = sv.LabelAnnotator()
    bounding_box_annotator = sv.BoundingBoxAnnotator()

    image = cv2.imread(image_path)

    # Modify image
    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)

    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    annotated_image = draw_center_dots(annotated_image, data)
    annotated_image = draw_dead_zones(annotated_image, dead_zones, crop_fix)

    cv2.imwrite(f'./{folder}/round_{current}.jpg', annotated_image)


def get_predictions(folder, filename):
    predictions = get_webui_predictions(f"./{folder}/{filename}")

    return predictions


def filter_by_confidence(data, confidence):
    data["predictions"] = \
        [p for p in data["predictions"] if p["confidence"] >= confidence]

    return data


def sort_by_click_order(data, sort_type):
    if sort_type == "random":
        # Press randomly
        random.shuffle(data["predictions"])
    elif sort_type == "top_to_bottom":
        # Press top to bottom, right to left
        data["predictions"] = sorted(
            data["predictions"], key=lambda p: (p['y'], -p['x']))

    return data


def save_prediction_data(folder, data):
    with open(f"./{folder}/current_predictions.json", 'w') as f:
        json.dump([data], f)


def is_point_in_box(point, box):
    # Check if a point is within a box
    x, y = point
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def get_wanted_clicks(data, crop_fix, dead_zones):
    clicks = [(box["x"], box["y"] + crop_fix)
              for box in data["predictions"]]

    filtered_clicks = []
    for click in clicks:
        # Add click to filtered_clicks if it's not in any of the dead zones
        if not any(is_point_in_box(click, box) for box in dead_zones):
            filtered_clicks.append(click)

    return filtered_clicks
