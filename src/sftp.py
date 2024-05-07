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
from typing import Optional
from pathlib import Path
from returns.result import Result, Success, Failure, safe

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SFTPClient:
    def __init__(self, hostname: str, port: int, username: str, password: str) -> None:
        """
        Inicializa o cliente SFTP com as credenciais fornecidas.
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.transport: Optional[paramiko.Transport] = None
        self.sftp: Optional[paramiko.SFTPClient] = None

    def __enter__(self) -> "SFTPClient":
        self.connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        result = self.disconnect()

        if isinstance(result, Failure):
            logging.error("Failed to cleanly disconnect from SFTP.")

    @safe
    def connect(self) -> Result[None, Exception]:
        """
        Conecta ao servidor SFTP.
        """

        try:
            self.transport = paramiko.Transport((self.hostname, self.port))
            self.transport.connect(
                username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)

            logging.info(
                f"Connected to SFTP server at {self.hostname}:{self.port}")

            return Success(None)
        except Exception as e:
            logging.error(f"Failed operation [Detail: {str(e)}]")

            return Failure(e)

    @safe
    def disconnect(self) -> Result[None, Exception]:
        """
        Desconecta do servidor SFTP.
        """

        try:
            if self.sftp:
                self.sftp.close()

            if self.transport:
                self.transport.close()

            logging.info(
                f"Disconnected from SFTP server at {self.hostname}:{self.port}")

            return Success(None)
        except Exception as e:
            logging.error(f"Failed operation [Detail: {str(e)}]")

            return Failure(e)

    @safe
    def listdir(self, remote_path: str) -> Result[Optional[list], Exception]:
        """
        Lista o conteúdo do diretório remoto.
        """

        if self.sftp is None:
            return Failure(Exception("SFTP client not connected"))

        try:
            entries = self.sftp.listdir(remote_path)

            logging.info(f"Listing directory {remote_path}: {entries}")

            return Success(entries)
        except Exception as e:
            logging.error(f"Failed operation [Detail: {str(e)}]")

            return Failure(e)

    @safe
    def upload(self, local_path: str, remote_path: str) -> Result[None, Exception]:
        """
        Faz upload de um arquivo local para o caminho remoto.
        """

        local_path_obj = Path(local_path)

        if not local_path_obj.exists():
            return Failure(
                FileNotFoundError(f"Local file {local_path} does not exist.")
            )

        if not local_path_obj.is_file():
            return Failure(ValueError(f"Local path {local_path} is not a file."))

        if self.sftp is None:
            return Failure(Exception("SFTP client not connected"))

        try:
            self.sftp.put(local_path, remote_path)

            logging.info(f"Uploaded {local_path} to {remote_path}")

            return Success(None)
        except Exception as e:
            logging.error(f"Failed operation [Detail: {str(e)}]")

            return Failure(e)

    @safe
    def download(self, remote_path: str, local_path: str) -> Result[None, Exception]:
        """
        Faz download de um arquivo remoto para o caminho local.
        """

        if self.sftp is None:
            return Failure(Exception("SFTP client not connected"))

        try:
            self.sftp.get(remote_path, local_path)

            logging.info(f"Downloaded {remote_path} to {local_path}")

            return Success(None)
        except Exception as e:
            logging.error(f"Failed operation [Detail: {str(e)}]")

            return Failure(e)
