import os
import time

from adb_util import *
from model_util import *


FOLDER = "CookieClicker"
FILENAME = "screenshot.jpg"
CROP = True
CONFIDENCE = 0.35
ROUNDS = 20
SORT_TYPE = "random"
DEAD_ZONES = [(450, 2200, 1080, 2335)]


if __name__ == "__main__":
    start_adb_server()

    device = get_device()

    # Make Run Folder
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    for round in range(1, ROUNDS+1):
        print(f"Round: {round}")

        # Create screenshot
        removed_pixels = create_screenshot(
            device, name=FILENAME, folder=FOLDER, crop=CROP)

        # Turn on Pointer Location (for visualization)
        toggle_pointer_location(device, True)

        # Find where to click
        prediction_data = get_predictions(FOLDER, FILENAME)
        filtered_data = filter_by_confidence(prediction_data, CONFIDENCE)
        sorted_data = sort_by_click_order(filtered_data, SORT_TYPE)

        # Create the Highlight Image
        make_prediction_image(FOLDER, FILENAME, round,
                              sorted_data, DEAD_ZONES, removed_pixels)

        # Save Predictions
        save_prediction_data(FOLDER, sorted_data)

        clicks = get_wanted_clicks(sorted_data, removed_pixels, DEAD_ZONES)

        # Make the Clicks
        for x, y in clicks:
            print(x, y)

            tap_screen(device, x, y, 1000)
            time.sleep(0.33)
