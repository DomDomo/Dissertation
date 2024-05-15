import json
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

MODEL = "webui"
GROUND_TRUTH_FOLDER = "ground_truth"
PREDICTIONS_FOLDER = f"predictions/{MODEL}"
PREDICTIONS_FILE = f"{MODEL}_predictions.json"
ZONES_FILE = "zones.json"
EVALUATION_RESULTS_FILE = "evaluation_results.json"
CENTER_DOTS_FOLDER = f"./{PREDICTIONS_FOLDER}/images"


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


def process_image(image_data, game, truth_zones, crop_fix, predictions):
    filename = image_data["title"]
    true_image_path = os.path.join(
        GROUND_TRUTH_FOLDER, game, f"true_{filename}.jpg")
    true_image = cv2.imread(true_image_path)

    image = {
        "data": true_image.copy(),
        "matched_truth_zones": set()
    }

    title = f"{game}_{filename}"
    preds = next((obj for obj in predictions if obj["title"] == title), None)

    if preds:
        centers = [(pred["x"], pred["y"], pred["confidence"])
                   for pred in preds["predictions"]]
        centers.sort(key=lambda x: x[2], reverse=True)

        for center in centers:
            draw_prediction(image, center, truth_zones, crop_fix)

    output_path = os.path.join(
        CENTER_DOTS_FOLDER, f"{game}_result_{filename}.jpg")
    cv2.imwrite(output_path, image["data"])


def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * precision * recall / \
        (precision + recall) if precision + recall > 0 else 0
    return precision, recall, f1_score


def evaluate_image(image_data, game, truth_zones, crop_fix, predictions, confidence_threshold):
    tp = fp = 0
    matched_truth_zones = set()

    title = f"{game}_{image_data['title']}"
    preds = next((obj for obj in predictions if obj["title"] == title), None)

    if preds:
        for pred in preds["predictions"]:
            if pred["confidence"] >= confidence_threshold:
                x, y = pred["x"], pred["y"]
                is_tp = False
                for i, truth_zone in enumerate(truth_zones):
                    if is_center_inside((x, y), truth_zone, crop_fix):
                        if i not in matched_truth_zones:
                            is_tp = True
                            matched_truth_zones.add(i)
                        break

                if is_tp:
                    tp += 1
                else:
                    fp += 1

    fn = len(truth_zones) - len(matched_truth_zones)
    return tp, fp, fn


def evaluate_confidence_thresholds(truth_data, predictions):
    confidence_thresholds = np.arange(0, 0.95, 0.1)
    evaluation_results = []

    for confidence_threshold in confidence_thresholds:
        total_tp = total_fp = total_fn = 0

        for game, game_data in truth_data.items():
            crop_fix = game_data["crop_fix"]

            for image_data in game_data["images"]:
                truth_zones = image_data["zones"]
                tp, fp, fn = evaluate_image(
                    image_data, game, truth_zones, crop_fix, predictions, confidence_threshold)
                total_tp += tp
                total_fp += fp
                total_fn += fn

        precision = total_tp / \
            (total_tp + total_fp) if total_tp + total_fp > 0 else 0
        recall = total_tp / \
            (total_tp + total_fn) if total_tp + total_fn > 0 else 0
        f1_score = 2 * precision * recall / \
            (precision + recall) if precision + recall > 0 else 0

        evaluation_results.append({
            'confidence_threshold': confidence_threshold,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        })

    return evaluation_results


def plot_evaluation_results(evaluation_results):
    confidence_thresholds = [result['confidence_threshold']
                             for result in evaluation_results]
    precisions = [result['precision'] for result in evaluation_results]
    recalls = [result['recall'] for result in evaluation_results]
    f1_scores = [result['f1_score'] for result in evaluation_results]

    plt.figure(figsize=(10, 6))
    plt.plot(confidence_thresholds, precisions, marker='o', label='Precision')
    plt.plot(confidence_thresholds, recalls, marker='o', label='Recall')
    plt.plot(confidence_thresholds, f1_scores, marker='o', label='F1 Score')

    plt.xlabel('Confidence Threshold')
    plt.ylabel('Score')
    plt.title('Evaluation Metrics vs Confidence Threshold')

    plt.legend(loc='upper right')

    plt.grid(True)
    plt.xticks(confidence_thresholds)
    plt.yticks(np.arange(0, 1.1, 0.1))

    plt.savefig(os.path.join(PREDICTIONS_FOLDER, 'evaluation_graph.png'))
    plt.close()


def main_generate_images():
    with open(os.path.join(GROUND_TRUTH_FOLDER, ZONES_FILE), 'r') as f:
        truth_data = json.load(f)

    with open(os.path.join(PREDICTIONS_FOLDER, PREDICTIONS_FILE), 'r') as f:
        predictions = json.load(f)

    os.makedirs(CENTER_DOTS_FOLDER, exist_ok=True)

    for game, game_data in truth_data.items():
        crop_fix = game_data["crop_fix"]

        for image_data in game_data["images"]:
            truth_zones = image_data["zones"]
            process_image(image_data, game, truth_zones, crop_fix, predictions)

    print("Images with center dots generated successfully.")


def main_evaluate_thresholds():
    with open(os.path.join(GROUND_TRUTH_FOLDER, ZONES_FILE), 'r') as f:
        truth_data = json.load(f)

    with open(os.path.join(PREDICTIONS_FOLDER, PREDICTIONS_FILE), 'r') as f:
        predictions = json.load(f)

    evaluation_results = evaluate_confidence_thresholds(
        truth_data, predictions)

    with open(os.path.join(PREDICTIONS_FOLDER, EVALUATION_RESULTS_FILE), 'w') as f:
        json.dump(evaluation_results, f, indent=4)

    plot_evaluation_results(evaluation_results)

    print("Evaluation results saved and graph generated.")
    plt.show()


if __name__ == "__main__":
    main_generate_images()
    main_evaluate_thresholds()
