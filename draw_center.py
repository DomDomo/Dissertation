import supervision as sv
import json
import cv2


def draw_center_dots(image, pred):
    for prediction in pred["predictions"]:
        # Draw a red dot at the center point
        cv2.circle(image, (prediction["x"], prediction["y"]), radius=5, color=(
            255, 0, 0), thickness=-1)

    return image


def make_prediction_image(current, confidence, folder):
    with open(f"./{folder}/current_predictions.json", 'r') as f:
        data = json.load(f)

    pred = data[0]
    image_path = data[0]["image"]["path"]

    pred["predictions"] = \
        [p for p in pred["predictions"] if p["confidence"] >= confidence]

    labels = [str(round(p["confidence"], 5)) for p in pred["predictions"]]
    detections = sv.Detections.from_inference(pred)

    label_annotator = sv.LabelAnnotator()
    bounding_box_annotator = sv.BoundingBoxAnnotator()

    image = cv2.imread(image_path)

    # Modify image
    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)

    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    annotated_image = draw_center_dots(annotated_image, pred)

    cv2.imwrite(f'./{folder}/round_{current}.jpg', annotated_image)
