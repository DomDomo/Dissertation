import time
from util import *


if __name__ == "__main__":
    start_adb_server()

    device = get_device()

    # toggle_pointer_location(device)

    # for _ in range(50):
    #     tap_screen(device, 500, 1000)

    # randomly_tap(device, count=200, delay=0.1)

    create_screenshot(device, name="main",
                      crop=False, image_format="jpg")
