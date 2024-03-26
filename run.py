import time
import json
import random
from util import *

from models.webui.webui import get_webui_predictions
from draw_center import make_prediction_image

def get_wanted_clicks(filename, crop_fix, confidence):

    predictions = get_webui_predictions(f"./{filename}")
    predictions["predictions"] = \
        [p for p in predictions["predictions"] if p["confidence"] >= confidence]
    
    # Want to press top to bottom, right to left
    predictions["predictions"] = sorted(predictions["predictions"], key=lambda p: (p['y'], -p['x']))

    # random.shuffle(predictions["predictions"])
    
    with open(f"./current_predictions.json", 'w') as f:
        json.dump([predictions], f)


    clicks = [(box["x"], box["y"] + crop_fix) for box in predictions["predictions"]]


    return clicks


if __name__ == "__main__":
    start_adb_server()

    device = get_device()

    FILE_NAME = "screenshot"
    FORMAT = "jpg"
    CONFIDENCE = 0.45
    filename = f"{FILE_NAME}.{FORMAT}"


    for i in range(20):
        print(f"Round: {i}")

        toggle_pointer_location(device)
        pixels_to_remove = create_screenshot(device, name=FILE_NAME,
                        crop=False, image_format=FORMAT)
        toggle_pointer_location(device)

        clicks = get_wanted_clicks(filename, pixels_to_remove, CONFIDENCE)
        make_prediction_image(i, CONFIDENCE)
        
        for click in clicks:
            print(click)
            tap_screen(device, click[0], click[1], 1000)
            time.sleep(0.33)

    