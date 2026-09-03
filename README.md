# sftp-server-uploads

Servidor SFTP local (Ubuntu + OpenSSH via Docker) e dois clients independentes que o exercitam:
um em Python (`src/`, com `Result` via `returns`) e um em TypeScript (`src/ts/`, com `ssh2`).

## Servidor

```sh
cp .env.example .env   # defina SFTP_USER e SFTP_PASSWORD
docker-compose up --build -d
```

Sobe em `127.0.0.1:2222`. Os uploads são persistidos em `./data` (montado em
`/home/${SFTP_USER}/uploads` no container).

## Client Python

```sh
python3 -m venv ./venv
source venv/bin/activate            # ou activate.fish
pip install -r requirements.txt     # requirements-dev.txt para mypy
```

```sh
SFTP_USER=... SFTP_PASSWORD=... python3 src/main.py
```

Type check: `mypy`

## Client TypeScript

```sh
cd src/ts
npm ci
```

```sh
SFTP_USER=... SFTP_PASSWORD=... npm run example
```

Type check: `npm run typecheck`
