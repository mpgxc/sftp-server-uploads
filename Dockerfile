FROM ubuntu:24.04

ARG SFTP_USER
# SFTP_PASSWORD não é usado no build: a senha é aplicada pelo entrypoint.sh em
# tempo de execução, que também valida se ela foi definida.
ARG SFTP_PASSWORD

# Falha antes do apt-get (que leva dezenas de segundos) quando o .env foi
# copiado do .env.example mas não preenchido — sem isso o `useradd` abaixo
# receberia um nome de usuário vazio e falharia com um "Usage:" críptico.
RUN test -n "${SFTP_USER}" || { \
        echo "ERRO: SFTP_USER está vazio. Defina SFTP_USER e SFTP_PASSWORD no arquivo .env (veja .env.example)."; \
        exit 1; \
    }

# Instalando o servidor SSH e criando o usuário sftp (sem privilégio de sudo)
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -rm -d /home/${SFTP_USER} -s /bin/bash -u 1001 ${SFTP_USER}

# Configurando o servidor SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Criando um diretório para a separação de privilégios do SSH
RUN mkdir /run/sshd

# Expondo a porta 22 para SSH
EXPOSE 22

# Copiando script de inicialização e definindo permissões
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
