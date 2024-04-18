import cv2


FOLDER = "ground_truth/CookieClicker"
FILENAME = "upgrades.jpg"
TRUTH_ZONES = [

    (705, 315, 855, 465),
    (865, 315, 1015, 465),

    (705, 480, 855, 630),
    (865, 480, 1015, 630),

    (705, 645, 855, 795),
    (865, 645, 1015, 795),

    (705, 810, 855, 960),
    (865, 810, 1015, 960),


    (25, 2010, 240, 2170),
    (240, 2010, 460, 2170),

    (715, 2090, 1040, 2170),

    (30, 2200, 190, 2335),
    (260, 2175, 395, 2335),
    (460, 2200, 635, 2340),
    (685, 2200, 820, 2340),
    (910, 2200, 1045, 2340),
]
FIX = 120


def draw_truth_zones(image, truth_zones):
    overlay = image.copy()
    opacity = 0.5

    for box in truth_zones:
        top_left = (box[0], box[1] - FIX)
        bottom_right = (box[2], box[3] - FIX)
        cv2.rectangle(overlay, top_left, bottom_right,
                      (0, 255, 0), -1)  # -1 fills the rectangle

    # Blend the original image with the overlay
    cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return image


if __name__ == "__main__":
    image = cv2.imread(f"./{FOLDER}/{FILENAME}")

    annotated_image = draw_truth_zones(image, TRUTH_ZONES)

    cv2.imwrite(f'./{FOLDER}/true_{FILENAME}', annotated_image)
