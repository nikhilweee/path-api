import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

LEGACY_CONFIGURATION_DECRYPT_KEY = "TLckjEE2f4mdo6d6vqiHhgTfB"
CONFIGURATION_DECRYPT_KEY = "PVTG16QwdKSbQhjIwSsQdAm0i"
KEY_SALT = bytes([73, 118, 97, 110, 32, 77, 101, 100, 118, 101, 100, 101, 118])


def decrypt(cipher_text: str, legacy_key: bool = False) -> str:
    """
    Decrypts the provided base64-encoded string.

    Args:
        cipher_text (str): The string to decrypt.
        legacy_key (bool): Whether to use the legacy key for decryption.

    Returns:
        str: The decrypted version of the input.
    """
    buffer = base64.b64decode(cipher_text.replace(" ", "+"))
    key = LEGACY_CONFIGURATION_DECRYPT_KEY if legacy_key else CONFIGURATION_DECRYPT_KEY

    kdf = PBKDF2(key, KEY_SALT, dkLen=48)  # 32 bytes for key, 16 for IV
    key = kdf[:32]
    iv = kdf[32:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(buffer), AES.block_size)

    return decrypted.decode("utf-16")
