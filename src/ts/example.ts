/**
 * Smoke test manual do client contra o servidor SFTP dockerizado.
 *
 * Credenciais vêm do ambiente (mesmos valores do `.env` usado no docker-compose):
 *
 *     SFTP_USER=... SFTP_PASSWORD=... npm run example
 */

import { basename } from "node:path";

import { SFTP } from "./sftp.js";

const requireEnv = (name: string): string => {
    const value = process.env[name];

    if (!value) {
        throw new Error(`Missing required environment variable: ${name}`);
    }

    return value;
};

const username = requireEnv("SFTP_USER");

const sftp = new SFTP({
    host: process.env.SFTP_HOST ?? "127.0.0.1",
    port: Number(process.env.SFTP_PORT ?? 2222),
    username,
    password: requireEnv("SFTP_PASSWORD"),
});

const remoteDir = process.env.SFTP_REMOTE_DIR ?? `/home/${username}/uploads`;
const localFile = process.env.SFTP_LOCAL_FILE ?? "../file.txt";
const remoteName = basename(localFile);

try {
    await sftp.connect();

    console.info(JSON.stringify(await sftp.listFiles(remoteDir), null, 2));

    await sftp.upload(localFile, `${remoteDir}/${remoteName}`);

    console.info(JSON.stringify(await sftp.listFiles(remoteDir), null, 2));
} catch (error) {
    console.error("Erro:", error);
    process.exitCode = 1;
} finally {
    await sftp.disconnect();
}
