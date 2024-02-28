import os
import time
import random
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


def get_screen_dimensions(device):
    output = device.shell("wm size")
    width, height = map(int, output.split()[-1].split("x"))
    return width, height


def create_screenshot(device):
    # Check if the screenshot file exists and delete it if it does
    if device.shell('test -f /sdcard/screenshot.png') == "":
        device.shell('rm /sdcard/screenshot.png')

    # Capture a screenshot
    device.shell('screencap -p /sdcard/screenshot.png')
    device.pull('/sdcard/screenshot.png', 'screenshot.png')
    device.shell('rm /sdcard/screenshot.png')


def randomly_tap(device, count, delay):
    width, height = get_screen_dimensions(device)

    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)

        device.shell(f"input touchscreen tap {x} {y}")

        time.sleep(delay)
