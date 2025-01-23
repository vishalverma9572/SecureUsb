import os
import subprocess
import json


def list_usb_devices():
    """Returns a list of all USB devices, including names and mount points."""
    devices = []

    # Run lsblk to get all block devices in JSON format
    result = subprocess.run("lsblk -J -o NAME,MOUNTPOINT,TRAN", shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            for device in data.get("blockdevices", []):
                # Check if the device is a USB (TRAN == 'usb')
                if device.get("tran") == "usb":
                    name = device["name"]
                    mountpoint = device.get("mountpoint", "Not Mounted")

                    # If there are partitions, check them
                    if "children" in device:
                        for child in device["children"]:
                            partition_name = child["name"]
                            partition_mount = child.get("mountpoint", "Not Mounted")
                            devices.append((partition_name, partition_mount))
                    else:
                        # If no partitions, add the main device
                        devices.append((name, mountpoint))

        except json.JSONDecodeError:
            print("Error parsing JSON output from lsblk.")
    print(devices)
    return devices


def check_public_partition(mount_point):
    """Checks if 123.txt exists in the public partition."""
    if mount_point == "Not Mounted":
        return False  # Skip unmounted devices

    file_path = os.path.join(mount_point, "123.txt")
    return os.path.exists(file_path)


# **Test Output:**
if __name__ == "__main__":
    devices = list_usb_devices()
    print("\nDetected USB Devices:")
    for device, mount in devices:
        print(f"Device: {device} | Mount Point: {mount}")

    # Check for 123.txt in each USB device
    for device, mount in devices:
        if check_public_partition(mount):
            print(f"✅ SecureUsb Drive in {device} at {mount}")
        else:
            print(f"❌ No SecureUsb file found in {device}.")
