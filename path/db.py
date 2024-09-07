import base64
import logging
import os
import sqlite3
import zipfile

import requests
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

logger = logging.getLogger(__name__)


def decrypt(cipher_text: str, legacy_key: bool = False) -> str:
    """
    Decrypts the provided base64-encoded string.

    Args:
        cipher_text: The string to decrypt.
        legacy_key: Whether to use the legacy key for decryption.

    Returns:
        The decrypted version of the input.
    """
    LEGACY_CONFIGURATION_DECRYPT_KEY = "TLckjEE2f4mdo6d6vqiHhgTfB"
    CONFIGURATION_DECRYPT_KEY = "PVTG16QwdKSbQhjIwSsQdAm0i"
    KEY_SALT = bytes([73, 118, 97, 110, 32, 77, 101, 100, 118, 101, 100, 101, 118])

    buffer = base64.b64decode(cipher_text.replace(" ", "+"))
    key = LEGACY_CONFIGURATION_DECRYPT_KEY if legacy_key else CONFIGURATION_DECRYPT_KEY

    kdf = PBKDF2(key, KEY_SALT, dkLen=48)  # 32 bytes for key, 16 for IV
    key = kdf[:32]
    iv = kdf[32:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(buffer), AES.block_size)

    return decrypted.decode("utf-16")


def fetch_latest_checksum(checksum="3672A87A4D8E9104E736C3F61023F013"):
    """Fetch the checksum of the most recent databse."""

    headers = {
        "apikey": "3CE6A27D-6A58-4CA5-A3ED-CE2EBAEFA166",
        "appname": "RidePATH",
        "appversion": "4.3.0",
        "user-agent": "okhttp/3.12.6",
        "dbchecksum": checksum,
    }

    url = "https://path-mppprod-app.azurewebsites.net/api/v1/Config/Fetch"
    response = requests.get(url, headers=headers)
    res_json = response.json()
    if "Checksum" in res_json["Data"]["DbUpdate"]:
        checksum = res_json["Data"]["DbUpdate"]["Checksum"]
    logger.info(f"fetched checksum: {checksum}")
    return checksum


def download_db(checksum="3672A87A4D8E9104E736C3F61023F013"):
    """Download and extract the database with the given checksum."""

    headers = {
        "apikey": "3CE6A27D-6A58-4CA5-A3ED-CE2EBAEFA166",
        "appname": "RidePATH",
        "appversion": "4.3.0",
        "user-agent": "okhttp/3.12.6",
    }
    url = f"https://path-mppprod-app.azurewebsites.net/api/v1/file/clientdb?checksum={checksum}"

    logger.info("downloading database: artifacts/db.sqlite.zip")
    response = requests.get(url, headers=headers)

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/db.sqlite.zip", "wb") as f:
        f.write(response.content)

    logger.info("extracting database: artifacts/db.sqlite")
    with zipfile.ZipFile("artifacts/db.sqlite.zip", "r") as zf:
        # Extract all contents into the folder
        name = zf.namelist().pop()
        zf.extract(name, "artifacts")

    os.rename(f"artifacts/{name}", "artifacts/db.sqlite")
    os.remove("artifacts/db.sqlite.zip")


def get_key_from_db(key):
    """Retrieve the value of a key from the configuration table."""
    con = sqlite3.connect("artifacts/db.sqlite")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT configuration_value FROM tblConfigurationData "
        f"WHERE configuration_key='{key}'"
    )
    value, *_ = res.fetchone()
    value = decrypt(value)
    logging.info(f"Decrypted {value}")
    return value


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_db(fetch_latest_checksum())
