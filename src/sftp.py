#!/usr/bin/env python3

"""
Author: Mateus Pinto Garcia
Email: mpgx5.c@gmail.com
Date: 2023-04-18
Co-author: Copilot

A client for connecting to an SFTP server and performing common operations such as
listing directory contents, uploading, and downloading files.
"""

import logging
import paramiko
from paramiko.ssh_exception import SSHException
from typing import Optional
from pathlib import Path

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SFTPClient:
    def __init__(self, hostname: str, port: int, username: str, password: str) -> None:
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.transport: Optional[paramiko.Transport] = None
        self.sftp: Optional[paramiko.SFTPClient] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self) -> None:
        try:
            self.transport = paramiko.Transport((self.hostname, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except SSHException as e:
            logging.error(f"Connection failed: {e}")
            raise

    def disconnect(self) -> None:
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()

    def listdir(self, remote_path: str) -> None:
        try:
            if self.sftp:
                entries = self.sftp.listdir(remote_path)
                for entry in entries:
                    logging.info(entry)
            else:
                logging.warning("Not connected")
        except FileNotFoundError:
            logging.error(f"Path {remote_path} not found")

    def upload(self, local_path: str, remote_path: str) -> None:
        try:
            local_path_obj = Path(local_path)
            if not local_path_obj.exists():
                logging.error(f"Local file {local_path} does not exist.")
                return

            if self.sftp:
                self.sftp.put(local_path, remote_path)
                logging.info(f"Uploaded {local_path} to {remote_path}")
            else:
                logging.warning("Not connected")
        except Exception as e:
            logging.error(f"Failed to upload {local_path} to {remote_path}: {e}")

    def download(self, remote_path: str, local_path: str) -> None:
        try:
            if self.sftp:
                self.sftp.get(remote_path, local_path)
                logging.info(f"Downloaded {remote_path} to {local_path}")
            else:
                logging.warning("Not connected")
        except Exception as e:
            logging.error(f"Failed to download {remote_path} to {local_path}: {e}")
