#!/bin/bash

# Configurar nome de usuário e senha
echo "Setting up SFTP user and password"
echo "$SFTP_USER:$SFTP_PASSWORD" | chpasswd

# Iniciar o servidor SSH
/usr/sbin/sshd -D
