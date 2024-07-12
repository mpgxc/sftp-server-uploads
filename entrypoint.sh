#!/bin/bash
set -e

# Configurar nome de usuário e senha
echo "Setting up SFTP user and password"
echo "$SFTP_USER:$SFTP_PASSWORD" | chpasswd

# Criando o diretório de uploads e configurando permissões
mkdir -p /home/${SFTP_USER}/uploads \
    && chown ${SFTP_USER}:root /home/${SFTP_USER}/uploads \
    && chmod 775 /home/${SFTP_USER}/uploads

# Verificando permissões
ls -ld /home/${SFTP_USER}/uploads

# Iniciar o servidor SSH
/usr/sbin/sshd -D
