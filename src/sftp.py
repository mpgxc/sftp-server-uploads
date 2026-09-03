#!/usr/bin/env python3

"""
Author: Mateus Pinto Garcia
Email: mpgx5.c@gmail.com
Date: 2023-04-18
Co-author: Copilot

A client for connecting to an SFTP server and performing common operations such as
listing directory contents, uploading, and downloading files.

Todas as operações públicas são decoradas com `@safe`, portanto retornam
`Result[..., Exception]` (`Success`/`Failure`) em vez de propagar exceções.
"""

from __future__ import annotations

import logging
from pathlib import Path
from types import TracebackType
from typing import List, Optional

import paramiko
from returns.result import Failure, safe

logger = logging.getLogger(__name__)


class SFTPError(Exception):
    """Erro base do cliente SFTP."""


class NotConnectedError(SFTPError):
    """Levantado quando uma operação é solicitada sem conexão ativa."""


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
        self.connect().unwrap()

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        result = self.disconnect()

        if isinstance(result, Failure):
            logger.error("Failed to cleanly disconnect from SFTP.")

    def _require_sftp(self) -> paramiko.SFTPClient:
        """
        Devolve a sessão SFTP ativa ou falha se o cliente não estiver conectado.
        """

        if self.sftp is None:
            raise NotConnectedError("SFTP client not connected")

        return self.sftp

    @safe
    def connect(self) -> None:
        """
        Conecta ao servidor SFTP.
        """

        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username=self.username, password=self.password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        if sftp is None:
            transport.close()

            raise SFTPError("Could not open an SFTP session over the transport")

        self.transport = transport
        self.sftp = sftp

        logger.info("Connected to SFTP server at %s:%s", self.hostname, self.port)

    @safe
    def disconnect(self) -> None:
        """
        Desconecta do servidor SFTP.
        """

        if self.sftp is not None:
            self.sftp.close()
            self.sftp = None

        if self.transport is not None:
            self.transport.close()
            self.transport = None

        logger.info("Disconnected from SFTP server at %s:%s", self.hostname, self.port)

    @safe
    def listdir(self, remote_path: str) -> List[str]:
        """
        Lista o conteúdo do diretório remoto.
        """

        entries = self._require_sftp().listdir(remote_path)

        logger.info("Listing directory %s: %s", remote_path, entries)

        return entries

    @safe
    def upload(self, local_path: str, remote_path: str) -> None:
        """
        Faz upload de um arquivo local para o caminho remoto.
        """

        source = Path(local_path)

        if not source.exists():
            raise FileNotFoundError(f"Local file {local_path} does not exist.")

        if not source.is_file():
            raise ValueError(f"Local path {local_path} is not a file.")

        self._require_sftp().put(local_path, remote_path)

        logger.info("Uploaded %s to %s", local_path, remote_path)

    @safe
    def download(self, remote_path: str, local_path: str) -> None:
        """
        Faz download de um arquivo remoto para o caminho local.
        """

        self._require_sftp().get(remote_path, local_path)

        logger.info("Downloaded %s to %s", remote_path, local_path)
