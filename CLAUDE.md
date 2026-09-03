# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A local SFTP server (via Docker) plus two independent client implementations used to exercise it: a Python client (`src/`) and a TypeScript client (`src/ts/`). There is no shared build — the Docker server and the two clients are separate, standalone pieces wired together only by matching host/port/credentials.

## Running the SFTP server

```sh
cp .env.example .env   # set SFTP_USER and SFTP_PASSWORD
docker-compose up --build -d
```

The compose setup builds an Ubuntu + OpenSSH image (`Dockerfile`), creates the SFTP user via `entrypoint.sh`, and exposes the server on host port `2222` (mapped to container port `22`). Uploaded files land in `./data` on the host, mounted to `/home/${SFTP_USER}/uploads` in the container.

## Python client (`src/`)

Setup:
```sh
python3 -m venv ./venv
source venv/bin/activate            # or activate.fish
pip install -r requirements.txt     # requirements-dev.txt adds mypy + type stubs
```

Run (credentials come from the environment, matching `.env`):
```sh
SFTP_USER=... SFTP_PASSWORD=... python3 src/main.py
```

Type check: `mypy` (config in `mypy.ini` — it sets `files = src`, `mypy_path = src`, `disallow_untyped_defs`, and enables the `returns` mypy plugin needed for `Result` types to check correctly).

- `src/sftp.py` — `SFTPClient` wraps `paramiko.Transport`/`paramiko.SFTPClient`. Every public method (`connect`, `disconnect`, `listdir`, `upload`, `download`) is decorated with `@safe` from `returns`, so they return `Result[..., Exception]` (`Success`/`Failure`) instead of raising. **The `@safe` decorator is the only error-handling layer** — inside these methods, signal failure by raising (e.g. `NotConnectedError`, `FileNotFoundError`) and let `@safe` convert it to a `Failure`; do not add `try/except` that returns `Failure` manually, that duplicates what the decorator already does. Module-level errors: `SFTPError` (base) and `NotConnectedError`. The class is also a context manager (`with SFTPClient(...) as client:`), where `__enter__` unwraps the connect result so a failed connection raises.
- `src/main.py` — runnable smoke test against the Dockerized server: connect/listdir/upload/listdir/disconnect. Reads `SFTP_USER`/`SFTP_PASSWORD` (required) and optional `SFTP_HOST`/`SFTP_PORT`/`SFTP_REMOTE_DIR`. This is the only place that calls `logging.basicConfig` — `src/sftp.py` uses a module logger and does not configure logging on import.
- `src/file.txt` is the fixture the smoke tests upload; both clients reference it.
- There is no `src/__init__.py` on purpose: the scripts import each other flatly (`from sftp import ...`), and adding one makes mypy see `src/sftp.py` under two module names.

## TypeScript client (`src/ts/`)

```sh
cd src/ts
npm ci
SFTP_USER=... SFTP_PASSWORD=... npm run example
npm run typecheck   # tsc --noEmit, strict
```

- `sftp.ts` — the `SFTP` class built on `ssh2` (`Client`/`SFTPWrapper`), with `connect`/`disconnect`/`upload`/`download`/`listFiles`. Unlike the Python client, it throws/rejects on error (plain async/await, no Result type), using typed errors: `SFTPError` (base), `SFTPConnectionError`, `SFTPNotConnectedError`. `connect` removes its handshake listeners once settled and then attaches a persistent `error` listener — post-handshake errors would otherwise become an uncaught exception; the stored error surfaces on the next operation via `requireSftp()`. `disconnect` awaits the `close` event, so it is safe to await before the process exits.
- `example.ts` — the runnable smoke test (connect, list, upload, list, disconnect), reading the same env vars as `src/main.py` plus optional `SFTP_LOCAL_FILE`. Keep the class in `sftp.ts` importable; don't move runnable example code back into it.
- `tsconfig.json` is `strict` + `noUncheckedIndexedAccess`, ESM/NodeNext — so relative imports need the `.js` extension (`./sftp.js`). No test runner or linter is configured; `tsx` runs TypeScript directly.

## CI

`.github/workflows/ci.yml` runs on push to `main` and on every PR: `npm ci && npm run typecheck` for the TS client, and `pip install -r requirements-dev.txt && mypy` for the Python one. Both must stay green.

## Key things to keep in mind when editing

- The Python and TypeScript clients are not meant to be kept in feature parity by any shared contract — they're separate demonstrations of the same idea using different error-handling styles (`Result`/`returns` vs. typed throws). Don't assume changing one should change the other unless asked.
- No credentials are hardcoded anywhere: both smoke tests read them from the environment, and `.env` is gitignored. Keep it that way.
- The `SFTP_USER`/`SFTP_PASSWORD` env vars flow through three places that must stay consistent: `.env` → `docker-compose.yml` (build args + container env) → `entrypoint.sh` (creates the OS user and chpasswd). `entrypoint.sh` fails fast if either is unset.
- The SFTP user is deliberately created without sudo and owns its own group; don't add it back to `sudo`/`root` groups to work around a permissions issue.
