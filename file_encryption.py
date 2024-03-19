from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def encrypt_file(filename, key):
    cipher_suite = Fernet(key)
    with open(filename, 'rb') as file:
        plaintext = file.read()
    encrypted_data = cipher_suite.encrypt(plaintext)
    with open(filename + '.encrypted', 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(encrypted_filename, key):
    cipher_suite = Fernet(key)
    with open(encrypted_filename, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    # Determine the decrypted filename
    if encrypted_filename.endswith('.encrypted'):
        decrypted_filename = encrypted_filename[:-10]  # Remove the '.encrypted' suffix
    else:
        decrypted_filename = encrypted_filename + '.decrypted'  # Add a suffix to indicate decryption

    with open(decrypted_filename, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)


