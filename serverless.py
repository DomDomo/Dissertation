import os
from adb_shell.adb_device import AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner


def kill_adb_server():
    # Check if the ADB server is running
    adb_server_running = os.system('adb devices') == 0

    # Kill the ADB server if it was running
    if adb_server_running:
        os.system('adb kill-server')


# Check and kill the ADB server
kill_adb_server()

# Make the RSA singer
priv = open(r'C:\Users\Dom\.android\adbkey', 'rb').read()
pub = open(r'C:\Users\Dom\.android\adbkey.pub', 'rb').read()
signer = PythonRSASigner(pub, priv)

# Connect to the device
device = AdbDeviceUsb()
device.connect(rsa_keys=[signer], auth_timeout_s=0.1)


def create_screenshot():
    # Check if the screenshot file exists and delete it if it does
    if device.shell('test -f /sdcard/screenshot.png') == "":
        device.shell('rm /sdcard/screenshot.png')
    # Capture a screenshot
    device.shell('screencap -p /sdcard/screenshot.png')
    device.pull('/sdcard/screenshot.png', 'screenshot.png')
    device.shell('rm /sdcard/screenshot.png')


# Test swipe command
response = device.shell('input touchscreen swipe 800 1500 100 1500 100')
