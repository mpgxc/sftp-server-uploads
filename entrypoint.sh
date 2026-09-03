#!/bin/bash
set -euo pipefail

# Validando as credenciais recebidas via ambiente
: "${SFTP_USER:?SFTP_USER is required (defina no arquivo .env)}"
: "${SFTP_PASSWORD:?SFTP_PASSWORD is required (defina no arquivo .env)}"

# Configurar nome de usuário e senha
echo "Setting up SFTP user and password"
echo "$SFTP_USER:$SFTP_PASSWORD" | chpasswd

# Criando o diretório de uploads e configurando permissões
mkdir -p "/home/${SFTP_USER}/uploads"
chown "${SFTP_USER}:${SFTP_USER}" "/home/${SFTP_USER}/uploads"
chmod 755 "/home/${SFTP_USER}/uploads"

# Verificando permissões
ls -ld "/home/${SFTP_USER}/uploads"

# Iniciar o servidor SSH
exec /usr/sbin/sshd -D
