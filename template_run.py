import os
import time
import cv2
from util.adb_util import *
from util.model_util import *

FOLDER = "IdleSlayer"
FILENAME = "screenshot.jpg"
CROP = False
MODEL = "hallym"
CONFIDENCE = 0.2
SORT_TYPE = "random"
DEAD_ZONES = [(75, 500, 750, 2100)]
TEMPLATE_IMAGE = "./templates/slayer_coins.jpg"
TEMPLATE_THRESHOLD = 0.8
TEMPLATE_CLICK_COUNT = 50

# Time in seconds
CLICK_DURATION = 6 * 60  # 11 minutes
SCREENSHOT_INTERVALS = [60, 5 * 60]  # 1 minute, 5 minutes, 10 minutes


def check_for_generator(folder, screenshot_name, template_name, template_threshold):
    screenshot_path = os.path.join(folder, screenshot_name)
    template_path = template_name
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path, 0)
    result = cv2.matchTemplate(cv2.cvtColor(
        screenshot, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(max_val)

    if max_val >= template_threshold:
        top_left = max_loc
        bottom_right = (top_left[0] + template.shape[1],
                        top_left[1] + template.shape[0])
        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2
        return True, center_x, center_y

    return False, None, None


if __name__ == "__main__":
    start_adb_server()
    device = get_device()

    # Make Run Folder
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    start_time = time.time()
    next_screenshot_index = 0

    while time.time() - start_time < CLICK_DURATION:
        current_time = time.time()

        # Create screenshot at specified intervals
        if next_screenshot_index < len(SCREENSHOT_INTERVALS) and current_time - start_time >= SCREENSHOT_INTERVALS[next_screenshot_index]:
            create_screenshot(
                device, name=f"{CONFIDENCE}_{int(current_time)}.jpg", folder=FOLDER, crop=CROP)
            next_screenshot_index += 1

        # Create screenshot for processing
        removed_pixels = create_screenshot(
            device, name=FILENAME, folder=FOLDER, crop=CROP)

        # Turn on Pointer Location (for visualization)
        toggle_pointer_location(device, True)

        # Check for resource generation button
        contains_generator, gen_x, gen_y = check_for_generator(
            FOLDER, FILENAME, TEMPLATE_IMAGE, TEMPLATE_THRESHOLD)
        if contains_generator:
            for i in range(TEMPLATE_CLICK_COUNT):
                print(gen_x, gen_y)
                tap_screen(device, gen_x, gen_y)

        # Find where to click for upgrades
        prediction_data = get_predictions(FOLDER, FILENAME, MODEL)
        filtered_data = filter_by_confidence(prediction_data, CONFIDENCE)
        sorted_data = sort_by_click_order(filtered_data, SORT_TYPE)

        # Create the Highlight Image
        make_prediction_image(FOLDER, FILENAME, f"{current_time}",
                              sorted_data, DEAD_ZONES, removed_pixels)

        # Save Predictions
        save_prediction_data(FOLDER, sorted_data)

        clicks = get_wanted_clicks(sorted_data, removed_pixels, DEAD_ZONES)

        # Make the Clicks
        for x, y in clicks:
            print(x, y)
            tap_screen(device, x, y)
