FROM ubuntu:latest

ARG SFTP_USER
ARG SFTP_PASSWORD

# Instalando o servidor SSH e criando um usuário sftp
RUN apt-get update && apt-get install -y openssh-server \
  && useradd -rm -d /home/${SFTP_USER} -s /bin/bash -g root -G sudo -u 1001 ${SFTP_USER}

# Configurando o servidor SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
  && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Criando um diretório para a separação de privilégios do SSH
RUN mkdir /run/sshd

RUN mkdir -p /home/${SFTP_USER}/uploads
RUN chown ${SFTP_USER}:root /home/${SFTP_USER}/uploads
RUN chmod 775 /home/${SFTP_USER}/uploads

# Expondo a porta 22 para SSH
EXPOSE 22

# Copiando script de inicialização e definindo permissões
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
