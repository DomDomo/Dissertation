import os
import time
import random
from PIL import Image
from ppadb.client import Client as AdbClient


def start_adb_server():
    # Check if the ADB server is running
    adb_server_running = os.system('adb devices') == 0

    # Kill the ADB server if it was not running
    if not adb_server_running:
        os.system('adb start-server')


def get_device():
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()

    if len(devices) == 0:
        print('No devices attached')
        quit()

    return devices[0]


def toggle_pointer_location(device):
    # Get the current pointer location value
    current_value = int(device.shell(
        'settings get system pointer_location').strip())

    # Toggle the value
    new_value = 1 - current_value

    # Set the new value
    device.shell(f'settings put system pointer_location {new_value}')


def get_screen_dimensions(device):
    output = device.shell("wm size")
    width, height = map(int, output.split()[-1].split("x"))
    return width, height


def create_screenshot(device, name="screenshot", crop=False):
    # Check if the screenshot file exists and delete it if it does
    if device.shell(f'test -f /sdcard/{name}.png') == "":
        device.shell(f'rm /sdcard/{name}.png')

    # Capture and pull screenshot
    device.shell(f'screencap -p /sdcard/{name}.png')
    device.pull(f'/sdcard/{name}.png', f'{name}.png')

    # Delete screenshot from device
    device.shell(f'rm /sdcard/{name}.png')

    if crop:
        crop_notfication_bar(name)


def crop_notfication_bar(image_name):
    # Open image using PIL
    img = Image.open(f'{image_name}.png')
    width, height = img.size
    pixels = img.load()

    # Get the color of the top-left pixel
    top_color = pixels[0, 0]

    # Find the first row with a different color
    for y in range(height):
        if pixels[0, y] != top_color:
            break

    # Crop the image
    img_cropped = img.crop((0, y, width, height))

    # Save the cropped image
    img_cropped.save(f'{image_name}.png')


def tap_screen(device, x, y):
    device.shell(f"input touchscreen tap {x} {y}")


def randomly_tap(device, count, delay):
    width, height = get_screen_dimensions(device)

    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)

        tap_screen(device, x, y)

        time.sleep(delay)
