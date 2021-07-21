import os
from cryptography.fernet import Fernet


class AESenc(object):
    def __init__(self, key):
        self.key = key

    def encrypt_file(self, file_name):
        """
        Given a file name (str) , it encrypts the file and returns the name of the encrypted file
        """
        f = Fernet(self.key)
        with open(file_name, 'rb') as file:
            plaintext = file.read()
        enc = f.encrypt(plaintext)
        with open(file_name[:-4] + "_enc" + file_name[-4:], 'wb') as file:
            file.write(enc)
        return file_name[:-4] + "_enc" + file_name[-4:]

    def decrypt_file(self, file_name):
        """
        Given a file name (str) , it decrypts the file and returns the name of the decrypted file
        """
        f = Fernet(self.key)
        with open(file_name, 'rb') as file:
            ciphertext = file.read()
        dec = f.decrypt(ciphertext)
        with open(file_name[:-4] + "_dec" + file_name[-4:], 'wb') as file:
            file.write(dec)
        return file_name[:-4] + "_dec" + file_name[-4:]


def write_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    """
    Loads the key from the current directory named `key.key`
    """
    return open("key.key", "rb").read()


def test():
    write_key()
    key = load_key()
    enc = AESenc(key)
    file_name_enc = enc.encrypt_file(str(input("Enter name of file to encrypt: ")))
    input("file_name_enc = " + file_name_enc + "press something to continue")
    file_name_dec = enc.decrypt_file(str(input("Enter name of file to decrypt: ")))
    input("file_name_dec = " + file_name_dec + "press something to continue")
    os.remove(file_name_enc)
    os.remove(file_name_dec)


test()
