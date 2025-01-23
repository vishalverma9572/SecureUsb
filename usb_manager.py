import json
import subprocess

def list_usb_devices():
    """Lists connected USB devices with mount points."""
    try:
        result = subprocess.run(["lsblk", "-J", "-o", "NAME,MOUNTPOINT"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error executing lsblk")
            return []

        data = json.loads(result.stdout)
        devices = []

        def extract_devices(devices_list):
            """Recursively extract mounted USB devices."""
            for device in devices_list:
                mountpoint = device.get("mountpoint")
                if mountpoint and "/media" in str(mountpoint):
                    devices.append(f"{device['name']} → {mountpoint}")
                if "children" in device:
                    extract_devices(device["children"])

        extract_devices(data.get("blockdevices", []))
        return devices

    except Exception as e:
        print(f"Error listing USB devices: {e}")
        return []
