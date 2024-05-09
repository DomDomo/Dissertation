import os
import time

from util.adb_util import *
from util.model_util import *
from util.template_util import *
from util.display_util import *

FOLDER = "Games/IdleSlayer"
FILENAME = "screenshot.jpg"
CROP = False
MODEL = "webui"
CONFIDENCE = 0.3
SORT_TYPE = "random"
DEAD_ZONES = [(75, 500, 750, 2100), (540, 2115, 775, 2300)]
TEMPLATE_IMAGE = "./templates/slayer_coins.jpg"
TEMPLATE_THRESHOLD = 0.8
TEMPLATE_CLICK_COUNT = 50

# Time in seconds
CLICK_DURATION = 6 * 60  # 11 minutes
SCREENSHOT_INTERVALS = [60, 5 * 60]  # 1 minute, 5 minutes, 10 minutes


def run_setup():
    # Connect to device
    start_adb_server()
    device = get_device()

    # Make Run Folder
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    # Initialize the Model
    model = initialize_model(MODEL)

    # Initialize the DisplayManager
    display_manager = DisplayManager()

    # Make initial Screenshot
    removed_pixels = create_screenshot(
        device, FILENAME, FOLDER, CROP)

    return device, model, display_manager, removed_pixels


def make_screenshot(next_screenshot_index):
    # Create screenshot at specified intervals
    if next_screenshot_index < len(SCREENSHOT_INTERVALS) and current_time - start_time >= SCREENSHOT_INTERVALS[next_screenshot_index]:
        create_screenshot(
            device, f"{CONFIDENCE}_{current_time}.jpg", FOLDER, CROP)
        next_screenshot_index += 1

    # Create screenshot for processing
    create_screenshot(device, FILENAME, FOLDER, CROP)

    # Turn on Pointer Location (for visualization)
    toggle_pointer_location(device, True)


def click_generator():
    # Check for resource generation button
    contains_generator, gen_x, gen_y = check_for_generator(
        FOLDER, FILENAME, TEMPLATE_IMAGE, TEMPLATE_THRESHOLD)
    if contains_generator:
        for _ in range(TEMPLATE_CLICK_COUNT):
            print(gen_x, gen_y)
            tap_screen(device, gen_x, gen_y)


def get_upgrade_clicks(model, save=False):
    # Find where to click for upgrades
    prediction_data = get_predictions(FOLDER, FILENAME, MODEL, model)
    filtered_data = filter_by_confidence(prediction_data, CONFIDENCE)
    sorted_data = sort_by_click_order(filtered_data, SORT_TYPE)
    clicks = get_wanted_clicks(sorted_data, rp, DEAD_ZONES)

    if save:
        save_prediction_data(FOLDER, sorted_data)

    return clicks, sorted_data


def display_screenshots(text, folder, filename, annotated=None):
    image1 = Image.open(os.path.join(folder, filename))
    template = Image.open(TEMPLATE_IMAGE)

    if annotated is not None:
        image2 = Image.fromarray(annotated)
    else:
        image2 = image1

    dm.display_images(image1, image2, text, template)


if __name__ == "__main__":
    device, model, dm, rp = run_setup()

    start_time = time.time()
    next_screenshot_index = 0

    while time.time() - start_time < CLICK_DURATION:
        current_time = int(time.time())

        make_screenshot(next_screenshot_index)

        display_screenshots("Clicking Generator", FOLDER, FILENAME)

        click_generator()

        clicks, display_data = get_upgrade_clicks(model)

        # Create the Highlight Image
        annotated_image = make_prediction_image(
            FOLDER, FILENAME, current_time, display_data, DEAD_ZONES, rp)

        # Display the images
        display_screenshots("Clicking Upgrades", FOLDER,
                            FILENAME, annotated_image)

        # Make the Clicks
        for x, y in clicks:
            print(x, y)
            tap_screen(device, x, y)
