import subprocess

CRYPT_NAME = "encrypted_partition"
MOUNT_POINT = "/mnt/private_partition"

def unlock_luks_partition(device, password):
    """Unlocks a LUKS-encrypted USB partition."""
    try:
        subprocess.run(
            ["sudo", "cryptsetup", "luksOpen", f"/dev/{device}", CRYPT_NAME],
            input=password.encode(),
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def mount_partition():
    """Mounts the unlocked LUKS partition."""
    subprocess.run(["sudo", "mount", f"/dev/mapper/{CRYPT_NAME}", MOUNT_POINT], check=True)

def unmount_partition():
    """Unmounts the partition and closes LUKS."""
    subprocess.run(["sudo", "umount", MOUNT_POINT], check=True)
    subprocess.run(["sudo", "cryptsetup", "luksClose", CRYPT_NAME], check=True)
