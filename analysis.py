import json
import cv2
import os

GROUND_TRUTH_FOLDER = "ground_truth"
PREDICTIONS_FOLDER = "predictions"
PREDICTIONS_FILE = "webui_predictions.json"
ZONES_FILE = "zones.json"
EVALUATION_RESULTS_FILE = "evaluation_results.json"


def is_center_inside(center, box, fix):
    x, y = center
    y += fix
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def draw_prediction(image, center, truth_zones, fix):
    x, y, confidence = center
    is_tp = False
    is_duplicate = False

    for i, truth_zone in enumerate(truth_zones):
        if is_center_inside((x, y), truth_zone, fix):
            if i in image["matched_truth_zones"]:
                is_duplicate = True
            else:
                is_tp = True
                image["matched_truth_zones"].add(i)
            break

    color = (255, 0, 0) if is_tp else (
        0, 165, 255) if is_duplicate else (0, 0, 255)
    size = 10 if is_tp else 5

    cv2.circle(image["data"], (x, y), size, color, -1)
    cv2.putText(image["data"], f"Conf: {confidence:.2f}", (x + 10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    if is_tp:
        image["tp"] += 1
    else:
        image["fp"] += 1


def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * precision * recall / \
        (precision + recall) if precision + recall > 0 else 0
    return precision, recall, f1_score


def process_image(image_data, game, truth_zones, crop_fix, predictions):
    filename = image_data["title"]
    true_image_path = os.path.join(
        GROUND_TRUTH_FOLDER, game, f"true_{filename}.jpg")
    true_image = cv2.imread(true_image_path)

    image = {
        "data": true_image.copy(),
        "matched_truth_zones": set(),
        "tp": 0,
        "fp": 0
    }

    title = f"{game}_{filename}"
    preds = next((obj for obj in predictions if obj["title"] == title), None)

    if preds:
        centers = [(pred["x"], pred["y"], pred["confidence"])
                   for pred in preds["predictions"]]
        centers.sort(key=lambda x: x[2], reverse=True)

        for center in centers:
            draw_prediction(image, center, truth_zones, crop_fix)

    fn = len(truth_zones) - len(image["matched_truth_zones"])
    precision, recall, f1_score = calculate_metrics(
        image["tp"], image["fp"], fn)

    output_path = os.path.join(PREDICTIONS_FOLDER, f"{
                               game}_result_{filename}.jpg")
    cv2.imwrite(output_path, image["data"])

    return {
        "filename": filename,
        "true_positives": image["tp"],
        "false_positives": image["fp"],
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score
    }


def process_game(game, game_data, predictions):
    crop_fix = game_data["crop_fix"]
    game_results = []

    for image_data in game_data["images"]:
        truth_zones = image_data["zones"]
        result = process_image(
            image_data, game, truth_zones, crop_fix, predictions)
        game_results.append(result)

    return game_results


if __name__ == "__main__":
    with open(os.path.join(GROUND_TRUTH_FOLDER, ZONES_FILE), 'r') as f:
        truth_data = json.load(f)

    with open(os.path.join(PREDICTIONS_FOLDER, PREDICTIONS_FILE), 'r') as f:
        predictions = json.load(f)

    results = {}

    for game, game_data in truth_data.items():
        game_results = process_game(game, game_data, predictions)
        results[game] = game_results

    with open(os.path.join(PREDICTIONS_FOLDER, EVALUATION_RESULTS_FILE), 'w') as f:
        json.dump(results, f, indent=4)

    for game, game_results in results.items():
        print(f"Evaluation Metrics for {game}:")
        for result in game_results:
            print(f"  Filename: {result['filename']}")
            print(f"  True Positives (TP): {result['true_positives']}")
            print(f"  False Positives (FP): {result['false_positives']}")
            print(f"  False Negatives (FN): {result['false_negatives']}")
            print(f"  Precision: {result['precision']:.2f}")
            print(f"  Recall: {result['recall']:.2f}")
            print(f"  F1 Score: {result['f1_score']:.2f}")
            print()
        print()
