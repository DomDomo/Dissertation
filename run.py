import os
import time
import json
import random
from util import *

from models.webui.webui import get_webui_predictions
from draw_center import make_prediction_image


def get_wanted_clicks(filename, folder, crop_fix, confidence):

    predictions = get_webui_predictions(f"./{folder}/{filename}")
    predictions["predictions"] = \
        [p for p in predictions["predictions"] if p["confidence"] >= confidence]

    # Want to press top to bottom, right to left
    predictions["predictions"] = sorted(
        predictions["predictions"], key=lambda p: (p['y'], -p['x']))

    # random.shuffle(predictions["predictions"])

    with open(f"./{folder}/current_predictions.json", 'w') as f:
        json.dump([predictions], f)

    clicks = [(box["x"], box["y"] + crop_fix)
              for box in predictions["predictions"]]

    return clicks


if __name__ == "__main__":
    start_adb_server()

    device = get_device()

    FOLDER = "CookieClicker"
    FILENAME = "screenshot.jpg"
    CONFIDENCE = 0.45

    # Make Dump Folder
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    for i in range(1, 21):
        print(f"Round: {i}")

        # Create screenshot
        pixels_to_remove = create_screenshot(
            device, name=FILENAME, folder=FOLDER, crop=True)

        # Turn on Pointer Location
        toggle_pointer_location(device, True)

        # Find where to click
        clicks = get_wanted_clicks(
            FILENAME, FOLDER, pixels_to_remove, CONFIDENCE)

        # Create the Highlight Image
        make_prediction_image(i, CONFIDENCE, FOLDER)

        # Make the Clicks
        for x, y in clicks:
            print(x, y)

            tap_screen(device, x, y, 1000)
            time.sleep(0.33)
