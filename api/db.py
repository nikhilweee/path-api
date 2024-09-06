import os
import logging
import sqlite3
import requests
import zipfile
from api.crypto import decrypt

logger = logging.getLogger(__name__)


def fetch_latest_checksum(checksum="3672A87A4D8E9104E736C3F61023F013"):
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
    con = sqlite3.connect("artifacts/db.sqlite")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT configuration_value FROM tblConfigurationData "
        f"WHERE configuration_key='{key}'"
    )
    value, *_ = res.fetchone()
    value = decrypt(value)
    print("Decrypted", value)
    return value


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_db(fetch_latest_checksum())
