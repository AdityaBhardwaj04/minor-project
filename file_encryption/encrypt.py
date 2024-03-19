from cryptography.fernet import Fernet


# Generate a random encryption key
def generate_key():
    return Fernet.generate_key()


# Encrypt the contents of a file using the provided key
def encrypt_file(filename, key):
    cipher_suite = Fernet(key)  # Initialize a Fernet object with the encryption key
    with open(filename, 'rb') as file:
        plaintext = file.read()  # Read the plaintext data from the file
    encrypted_data = cipher_suite.encrypt(plaintext)  # Encrypt the plaintext data
    with open(filename + '.encrypted', 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)  # Write the encrypted data to a new file


# Generate an encryption key
key = generate_key()

# Specify the source file to be encrypted
source_file = 'plaintext.txt'

# Encrypt the file using the generated key
encrypt_file(source_file, key)

# Inform the user about the successful encryption
print(f'{source_file} encrypted.')  # Print a message indicating successful encryption

# Print the encrypted content in hexadecimal format
encrypted_filename = source_file + '.encrypted'
with open(encrypted_filename, 'rb') as encrypted_file:
    encrypted_data = encrypted_file.read()
    encrypted = encrypted_data.hex()
    # print("Encrypted Content:", encrypted)
