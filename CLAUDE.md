# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A local SFTP server (via Docker) plus two independent client implementations used to exercise it: a Python client (`src/`) and a TypeScript client (`src/ts/`). There is no shared build — the Docker server and the two clients are separate, standalone pieces wired together only by matching host/port/credentials.

## Running the SFTP server

```sh
docker-compose up --build -d
```

Requires `SFTP_USER` and `SFTP_PASSWORD` in a `.env` file (see `.env.example`). The compose setup builds an Ubuntu + OpenSSH image (`Dockerfile`), creates the SFTP user via `entrypoint.sh`, and exposes the server on host port `2222` (mapped to container port `22`). Uploaded files land in `./data` on the host, mounted to `/home/${SFTP_USER}/uploads` in the container.

## Python client (`src/`)

Setup:
```sh
python3 -m venv ./venv
source venv/bin/activate.fish   # or activate for bash/zsh
pip install -r requirements.txt
```

Run:
```sh
python3 src/main.py
```

Note: `requirements.txt` only lists `pysftp`, but `src/sftp.py` actually imports `paramiko` and `returns` — install those manually if missing when working in this file.

- `src/sftp.py` — `SFTPClient` wraps `paramiko.Transport`/`paramiko.SFTPClient`. Every public method (`connect`, `disconnect`, `listdir`, `upload`, `download`) is decorated with `@safe` from the `returns` library and returns a `Result[..., Exception]` (`Success`/`Failure`) rather than raising. Callers use `.unwrap()` or pattern-match on the `Result`. The class also supports use as a context manager (`with SFTPClient(...) as client:`).
- `src/main.py` — example/manual-test script that instantiates `SFTPClient` with hardcoded local credentials and calls connect/listdir/upload/listdir/disconnect against the Dockerized server on `127.0.0.1:2222`. Treat this as a runnable smoke test, not library code — paths and credentials inside are specific to the author's machine and need editing before running elsewhere.
- Type checking config lives in `mypy.ini` and enables the `returns` mypy plugin (needed for `Result` types to type-check correctly).

## TypeScript client (`src/ts/`)

```sh
cd src/ts
npm install
npm run run   # npx tsx sftp.ts
```

- `sftp.ts` — a minimal `SFTP` class built on the `ssh2` package (`Client`/`SFTPWrapper`), with `connect`/`disconnect`/`upload`/`listFiles`. Unlike the Python client, methods here throw/reject on error (plain async/await + Promise, no Result type). `upload` streams a local file to the remote path via `fs.createReadStream` piped through `stream/promises.pipeline`.
- The bottom of `sftp.ts` is a runnable example (connect, list, upload, disconnect) with hardcoded host/credentials — mirror of `src/main.py`'s role for this side.
- No test runner or linter is configured for this package; `tsx` is used to run TypeScript directly.

## Key things to keep in mind when editing

- The Python and TypeScript clients are not meant to be kept in feature parity by any shared contract — they're separate demonstrations of the same idea using different error-handling styles (`Result`/`returns` vs. throw/reject). Don't assume changing one should change the other unless asked.
- Example/entry scripts (`src/main.py`, bottom of `src/ts/sftp.ts`) contain hardcoded hosts, usernames, and passwords matching whatever `.env` was used to build the Docker server — update these together when changing credentials.
- The `SFTP_USER`/`SFTP_PASSWORD` env vars flow through three places that must stay consistent: `.env` → `docker-compose.yml` (build args + container env) → `entrypoint.sh` (creates the OS user and chpasswd).
