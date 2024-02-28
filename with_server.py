import os
from ppadb.client import Client as AdbClient


def start_adb_server():
    # Check if the ADB server is running
    adb_server_running = os.system('adb devices') == 0

    # Kill the ADB server if it was running
    if not adb_server_running:
        os.system('adb start-server')


# Check and start the ADB server
start_adb_server()

client = AdbClient(host="127.0.0.1", port=5037)
devices = client.devices()

if len(devices) == 0:
    print('no devices attached')
    quit()

device = devices[0]

device.shell('input touchscreen swipe 800 500 100 500 100')
