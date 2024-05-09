import os
import time

from util.adb_util import *
from util.model_util import *


FOLDER = "UniverstalPaperclips"
FILENAME = "screenshot.jpg"
CROP = False
CONFIDENCE = 0.35
SORT_TYPE = "random"
MAIN_CLICK = [255, 505]

# Time in seconds
CLICK_DURATION = 10 * 60  # 20 minutes
SCREENSHOT_INTERVAL = 1 * 60  # 5 minutes

if __name__ == "__main__":
    start_adb_server()

    device = get_device()

    # Make Run Folder
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    start_time = time.time()
    last_screenshot_time = start_time
    while time.time() - start_time < CLICK_DURATION:
        print(f"Clicking at: {MAIN_CLICK}")

        # Create screenshot at intervals
        if time.time() - last_screenshot_time >= SCREENSHOT_INTERVAL:
            create_screenshot(
                device, name=f"{int(time.time())}.jpg", folder=FOLDER, crop=CROP)
            last_screenshot_time = time.time()

        x, y = MAIN_CLICK[0], MAIN_CLICK[1]

        tap_screen(device, x, y, 1000)
    create_screenshot(
        device, name=f"{int(time.time())}.jpg", folder=FOLDER, crop=CROP)
