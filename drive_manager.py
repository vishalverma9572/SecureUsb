import os
import subprocess
import sys
import shutil
import io
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MOUNT_POINT = "/mnt/private_partition"
PARTITION = "/media/vishalkumar/7841-4163"  # Adjust this based on your setup
CRYPT_NAME = "encrypted_partition"  # Name for unlocked partition


def prompt_password():
    """Prompt the user to input the encryption password."""
    password = input("Enter the encryption password: ").strip()
    if not password:
        print("Password cannot be empty.")
        sys.exit(1)
    return password


def derive_key(password):
    """Derive a cryptographic key from a password using PBKDF2."""
    salt = b'some_salt'  # Should be stored securely and uniquely for each user/system
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def unlock_partition(password):
    """Unlock the LUKS-encrypted partition."""
    try:
        subprocess.run(
            ["sudo", "cryptsetup", "luksOpen", PARTITION, CRYPT_NAME],
            input=password.encode(), check=True
        )
        print("Partition unlocked successfully.")
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            print("Partition is already unlocked.")
        else:
            print(f"Failed to unlock partition: {e}")
            sys.exit(1)


def mount_partition():
    """Mount the unlocked partition with XFS filesystem detection."""
    if not os.path.exists(MOUNT_POINT):
        os.makedirs(MOUNT_POINT)
        print(f"Created mount point: {MOUNT_POINT}")

    try:
        subprocess.run(
            ["sudo", "mount", "-t", "xfs", f"/dev/mapper/{CRYPT_NAME}", MOUNT_POINT],
            check=True
        )
        print(f"Partition mounted successfully at {MOUNT_POINT}.")
    except subprocess.CalledProcessError:
        print("Mounting failed. The partition might not contain a valid XFS filesystem.")
        sys.exit(1)


def unmount_partition():
    """Forcefully unmount the partition and clean up."""
    try:
        print(f"Attempting to force unmount the partition at {MOUNT_POINT}...")
        subprocess.run(["sudo", "umount", "-f", MOUNT_POINT], check=True)
        print("Partition unmounted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to unmount the partition: {e}")


def encrypt_file(file_path, password):
    """Encrypt a file using AES."""
    key = derive_key(password)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    encrypted_file_path = file_path + ".enc"

    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + encrypted_data)

    return encrypted_file_path


def decrypt_file(file_path, password):
    """Decrypt a file using AES."""
    key = derive_key(password)

    with open(file_path, 'rb') as f:
        iv = f.read(16)  # Read the IV (16 bytes)
        encrypted_data = f.read()  # The encrypted data

    # Use the same padding and decryption logic as during encryption
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Ensure proper unpadding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data


def list_files():
    """List files in the mounted partition."""
    files = os.listdir(MOUNT_POINT)
    if files:
        print("Files in the partition:")
        for file in files:
            print(f" - {file}")
    else:
        print("No files found in the partition.")


def move_file(password):
    """Move and encrypt a file into the partition."""
    current_dir = os.getcwd()
    print(f"Files in the current directory ({current_dir}):")
    files = os.listdir(current_dir)

    if files:
        for file in files:
            print(f" - {file}")
        filename = input("Enter the name of the file to copy to the partition: ").strip()
        if filename in files:
            source = os.path.join(current_dir, filename)
            destination = os.path.join(MOUNT_POINT, "." + filename + ".enc")

            try:
                encrypted_file = encrypt_file(source, password)
                shutil.move(encrypted_file, destination)
                print(f"File '{filename}' encrypted and moved to the partition.")
            except Exception as e:
                print(f"Failed to encrypt and move file: {e}")
        else:
            print("File not found in the current directory.")
    else:
        print("No files found in the current directory.")


def open_file(password):
    """Decrypt and open a file from the partition."""
    print("Files in the partition:")
    files = os.listdir(MOUNT_POINT)

    if files:
        for file in files:
            print(f" - {file}")
        filename = input("Enter the name of the file to open: ").strip()
        if filename in files:
            file_path = os.path.join(MOUNT_POINT, filename)

            try:
                if file_path.endswith(".enc"):
                    decrypted_data = decrypt_file(file_path, password)
                    print(f"Decrypted file '{filename}'.")

                    with Image.open(io.BytesIO(decrypted_data)) as img:
                        img.show()
                else:
                    print(f"'{filename}' is not encrypted.")
            except Exception as e:
                print(f"Failed to open file: {e}")
        else:
            print("File not found in the partition.")
    else:
        print("No files found in the partition.")


def change_password():
    """Change the LUKS encryption password."""
    print("\nChanging LUKS encryption password...")
    current_password = prompt_password()
    new_password = input("Enter the new encryption password: ").strip()
    if not new_password:
        print("New password cannot be empty.")
        return

    confirm_password = input("Confirm the new password: ").strip()
    if new_password != confirm_password:
        print("Passwords do not match. Please try again.")
        return

    try:
        # Changing the LUKS password using cryptsetup
        subprocess.run(
            ["sudo", "cryptsetup", "luksChangeKey", PARTITION],
            input=f"{current_password}\n{new_password}\n".encode(),
            check=True
        )
        print("Password changed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to change the password: {e}")
        return


def main():
    password = prompt_password()
    unlock_partition(password)
    mount_partition()

    try:
        while True:
            print("\nOptions:")
            print("1. List files in the partition")
            print("2. Move and encrypt a file to the partition")
            print("3. Open and decrypt a file from the partition")
            print("4. Change the LUKS encryption password")
            print("5. Exit")
            choice = input("Enter your choice (1/2/3/4/5): ").strip()

            if choice == "1":
                list_files()
            elif choice == "2":
                move_file(password)
            elif choice == "3":
                open_file(password)
            elif choice == "4":
                change_password()
            elif choice == "5":
                print("Exiting...")
                unmount_partition()
                break
            else:
                print("Invalid choice. Try again.")
    except KeyboardInterrupt:
        print("\nCaught termination signal. Unmounting before exit...")
        unmount_partition()


if __name__ == "__main__":
    main()