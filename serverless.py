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

# Send a shell command
response = device.shell('input touchscreen swipe 800 500 100 500 100')
