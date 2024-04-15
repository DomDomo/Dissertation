import os
import time

from adb_util import *
from model_util import make_prediction_image, get_wanted_clicks


FOLDER = "CookieClicker"
FILENAME = "screenshot.jpg"
CONFIDENCE = 0.45

if __name__ == "__main__":
    start_adb_server()

    device = get_device()

    # Make Run Folder
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
