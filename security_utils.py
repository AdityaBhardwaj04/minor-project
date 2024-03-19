from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
import os
import hashlib
import json
import os
import hashlib
import base64

KEY_STORAGE_PATH = 'keys.json'  # File to store keys


def generate_key_store(username):
    user_key = hashlib.sha256(f"{username}some_secret_string".encode()).digest()  # Generate the key
    user_key_base64 = base64.b64encode(user_key).decode('utf-8')  # Convert to Base64 string

    try:
        # Load existing keys (if the file exists)
        if os.path.exists(KEY_STORAGE_PATH):
            with open(KEY_STORAGE_PATH, 'r') as f:
                user_keys = json.load(f)
        else:
            user_keys = {}

        # Store the new key (as a Base64 string)
        user_keys[username] = user_key_base64
        with open(KEY_STORAGE_PATH, 'w') as f:
            json.dump(user_keys, f)

    except (IOError, json.JSONDecodeError) as e:
        print(f"Error storing key: {e}")

    return user_key_base64  # Return the Base64 encoded key (you might need this elsewhere)


# def generate_key_store(username):
#     # ... (generate user_key)
#
#     try:
#         # Load existing keys (if the file exists)
#         if os.path.exists(KEY_STORAGE_PATH):
#             with open(KEY_STORAGE_PATH, 'r') as f:
#                 user_keys = json.load(f)
#         else:
#             user_keys = {}
#
#         # Store the new key
#         user_keys[username] = user_key
#         with open(KEY_STORAGE_PATH, 'w') as f:
#             json.dump(user_keys, f)
#
#     except (IOError, json.JSONDecodeError) as e:
#         print(f"Error storing key: {e}")
#
#     return user_key

# def generate_key_store(username):
#     user_key = hashlib.sha256(f"{username}some_secret_string".encode()).digest()  # Generate the key
#
#     try:
#         # Load existing keys (if the file exists)
#         if os.path.exists(KEY_STORAGE_PATH):
#             with open(KEY_STORAGE_PATH, 'r') as f:
#                 user_keys = json.load(f)
#         else:
#             user_keys = {}
#
#         # Store the new key
#         user_keys[username] = user_key
#         with open(KEY_STORAGE_PATH, 'w') as f:
#             json.dump(user_keys, f)
#
#     except (IOError, json.JSONDecodeError) as e:
#         print(f"Error storing key: {e}")
#
#     return user_key


def get_user_key(username):
    try:
        if os.path.exists(KEY_STORAGE_PATH):
            with open(KEY_STORAGE_PATH, 'r') as f:
                user_keys = json.load(f)
                return user_keys.get(username)
        else:
            return None  # No keys exist
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error retrieving key: {e}")
        return None


def encrypt_file(input_file, output_file, key):
    chunk_size = 64 * 1024
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        outfile.write(iv)
        while True:
            chunk = infile.read(chunk_size)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk += b' ' * (16 - (len(chunk) % 16))
            outfile.write(cipher.encrypt(chunk))


def decrypt_file(input_file, output_file, key):
    chunk_size = 64 * 1024
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        iv = infile.read(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        while True:
            chunk = infile.read(chunk_size)
            if len(chunk) == 0:
                break
            outfile.write(cipher.decrypt(chunk))


if __name__ == '__main__':
    username = 'testuser'
    user_key = generate_key_store(username)
    print("DEBUG: Encryption key:", user_key)
