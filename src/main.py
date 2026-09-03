#!/usr/bin/env python3

"""
Smoke test manual do `SFTPClient` contra o servidor SFTP dockerizado.

Credenciais vêm do ambiente (mesmos valores do `.env` usado no docker-compose):

    SFTP_USER=... SFTP_PASSWORD=... python3 src/main.py
"""

import logging
import os
from pathlib import Path

from sftp import SFTPClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

HOSTNAME = os.getenv("SFTP_HOST", "127.0.0.1")
PORT = int(os.getenv("SFTP_PORT", "2222"))
USERNAME = os.environ["SFTP_USER"]
PASSWORD = os.environ["SFTP_PASSWORD"]

LOCAL_FILE = Path(__file__).parent / "file.txt"
REMOTE_DIR = os.getenv("SFTP_REMOTE_DIR", f"/home/{USERNAME}/uploads")

if __name__ == "__main__":
    with SFTPClient(
        hostname=HOSTNAME,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
    ) as client:
        client.listdir(REMOTE_DIR).unwrap()
        client.upload(str(LOCAL_FILE), f"{REMOTE_DIR}/{LOCAL_FILE.name}").unwrap()
        client.listdir(REMOTE_DIR).unwrap()

        # Exemplo de uso:
        # client.download(f"{REMOTE_DIR}/file.txt", "/tmp/file.txt").unwrap()
