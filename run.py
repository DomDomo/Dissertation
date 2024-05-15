import os
import time

from util.adb_util import *
from util.model_util import *
from util.template_util import *
from util.display_util import *


# Game
GAME = "CookieClicker"
CROP = False

# Program
TEMPLATE_THRESHOLD = 0.9
TEMPLATE_CLICK_COUNT = 100
MODEL = "hallym"
CONFIDENCE = 0.1
SORT_TYPE = "random"

# Files
FOLDER = f"Games/{GAME}"
FILENAME = "screenshot.jpg"

# Time in seconds
CLICK_DURATION = 21 * 60  # 11 minutes
SCREENSHOT_INTERVALS = [60, 5 * 60, 10 * 60, 15 *
                        60, 20 * 60]  # 1 minute, 5 minutes, 10 minutes


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

    template, deadzones = get_game_data(GAME)

    return device, model, display_manager, removed_pixels, template, deadzones


def get_game_data(game):
    game_templates = {
        "IdleSlayer": {
            "template": "slayer_coins",
            "deadzones": [(75, 500, 450, 2100), (300, 2115, 775, 2300), (270, 510, 750, 1525), (340, 2000, 1015, 2080)]
        },
        "CookieClicker": {
            "template": "square_cookie",
            "deadzones": [(450, 2200, 1080, 2335), (250, 2000,
                                                    1040, 2170), (862, 320, 1015, 1952)]
        },
        "UniversalPaperclips": {
            "template": "MakePaperclip",
            "deadzones": [(1000, 60, 1065, 105)]
        },

        "ClickerHeroes": {
            "template": "ch_skull",
            "deadzones": [(20, 375, 150, 640), (70, 220,
                                                1000, 320), (190, 1480, 680, 2220), (15, 2250, 520, 2310), (0, 1360, 152, 1430)]
        },
    }

    template_name = game_templates[game]["template"]
    return f"./templates/{template_name}.jpg", game_templates[game]["deadzones"]


def make_screenshot(next_screenshot_index, start_time, current_time):
    print(next_screenshot_index)
    print((current_time - start_time))
    if next_screenshot_index < len(SCREENSHOT_INTERVALS) and (current_time - start_time) >= SCREENSHOT_INTERVALS[next_screenshot_index]:
        create_screenshot(
            device, f"{CONFIDENCE}_{current_time}.jpg", FOLDER, CROP)
        next_screenshot_index += 1

        return True

    # Create screenshot for processing
    create_screenshot(device, FILENAME, FOLDER, CROP)

    # Turn on Pointer Location (for visualization)
    toggle_pointer_location(device, True)

    return False


def click_generator(template):
    # Check for resource generation button
    contains_generator, gen_x, gen_y = check_for_generator(
        FOLDER, FILENAME, template, TEMPLATE_THRESHOLD)
    if contains_generator:
        for _ in range(TEMPLATE_CLICK_COUNT):
            print(gen_x, gen_y)
            tap_screen(device, gen_x, gen_y)


def get_upgrade_clicks(model, deadzones, save=False):
    # Find where to click for upgrades
    prediction_data = get_predictions(FOLDER, FILENAME, MODEL, model)
    filtered_data = filter_by_confidence(prediction_data, CONFIDENCE)
    sorted_data = sort_by_click_order(filtered_data, SORT_TYPE)
    clicks = get_wanted_clicks(sorted_data, rp, deadzones)

    if save:
        save_prediction_data(FOLDER, sorted_data)

    return clicks, sorted_data


def display_screenshots(text, folder, filename, template, annotated=None):
    image1 = Image.open(os.path.join(folder, filename))
    template = Image.open(template)

    if annotated is not None:
        image2 = Image.fromarray(annotated)
    else:
        image2 = image1

    dm.display_images(image1, image2, text, template)


if __name__ == "__main__":
    device, model, dm, rp, template, deadzones = run_setup()

    start_time = time.time()
    next_screenshot_index = 0

    while time.time() - start_time < CLICK_DURATION:
        current_time = int(time.time())

        made_interval_screenshot = make_screenshot(
            next_screenshot_index, start_time, current_time)
        if made_interval_screenshot:
            next_screenshot_index += 1

        display_screenshots("Clicking Generator", FOLDER, FILENAME, template)

        click_generator(template)

        clicks, display_data = get_upgrade_clicks(model, deadzones)

        # Create the Highlight Image
        annotated_image = make_prediction_image(
            FOLDER, FILENAME, current_time, display_data, deadzones, rp, save=True)

        # Display the images
        display_screenshots("Clicking Upgrades", FOLDER,
                            FILENAME, template, annotated_image)

        # Make the Clicks
        for x, y in clicks:
            # print(x, y)
            tap_screen(device, x, y)
