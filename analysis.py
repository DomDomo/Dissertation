import json
import cv2

GAME = "CookieClicker"
FOLDER = f"ground_truth/{GAME}"
FILENAME = "main"


def is_center_inside(center, box, fix):
    x, y = center
    y += fix
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def draw_predictions(image, centers, truth_zones, fix):
    matched_truth_zones = set()
    tp = 0
    fp = 0

    for i, center in enumerate(centers):
        x, y, confidence = center

        # Check if the center of the predicted bounding box is inside any truth zone
        is_tp = False
        is_duplicate = False
        for j, truth_zone in enumerate(truth_zones):
            if is_center_inside((x, y), truth_zone, fix):
                if j in matched_truth_zones:
                    is_duplicate = True
                else:
                    is_tp = True
                    matched_truth_zones.add(j)
                break

        # Set the color based on the correctness and duplication
        if is_tp:
            color = (255, 0, 0)  # Blue for correct guess on a new truth zone
            tp += 1
        elif is_duplicate:
            # Orange for correct guess on a duplicate truth zone
            color = (0, 165, 255)
            fp += 1
        else:
            color = (0, 0, 255)  # Red for incorrect guess
            fp += 1

        # Draw the center point of the predicted bounding box
        cv2.circle(image, (x, y), 5, color, -1)

        # Label the center point with confidence score
        label = f"Conf: {confidence:.2f}"
        cv2.putText(image, label, (x + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    fn = len(truth_zones) - len(matched_truth_zones)

    return image, tp, fp, fn


def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * (precision * recall) / (precision +
                                           recall) if precision + recall > 0 else 0

    return precision, recall, f1_score


if __name__ == "__main__":
    true_image = cv2.imread(f"./{FOLDER}/true_{FILENAME}.jpg")

    with open(f'./predictions/webui_predictions.json', 'r') as f:
        data = json.load(f)

    title = f"{GAME}_{FILENAME}"
    preds = [obj for obj in data if obj["title"] == title][0]

    centers = [(pred["x"], pred["y"], pred["confidence"])
               for pred in preds["predictions"]]
    centers.sort(key=lambda x: x[2], reverse=True)

    with open(f'./ground_truth/zones.json', 'r') as f:
        truth_data = json.load(f)

    true_game_zones = truth_data[GAME]
    truth_zones = [
        image for image in true_game_zones["images"] if image["title"] == FILENAME][0]["zones"]
    crop_fix = true_game_zones["crop_fix"]

    result_image, tp, fp, fn = draw_predictions(
        true_image.copy(), centers, truth_zones, crop_fix)

    cv2.imwrite(f'./predictions/result_{FILENAME}.jpg', result_image)

    precision, recall, f1_score = calculate_metrics(tp, fp, fn)

    print("Evaluation Metrics:")
    print(f"True Positives (TP): {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1_score:.2f}")
