import fs from "node:fs";
import { pipeline } from "node:stream/promises";
import { promisify } from "node:util";
import { Client, SFTPWrapper } from "ssh2";

export type Credentials = {
    host: string;
    port: number;
    username: string;
    password: string;
};

export class SFTPError extends Error {
    constructor(message: string, options?: ErrorOptions) {
        super(message, options);
        this.name = new.target.name;
    }
}

/** Falha no handshake/conexão com o servidor. */
export class SFTPConnectionError extends SFTPError {}

/** Operação solicitada sem uma sessão SFTP ativa. */
export class SFTPNotConnectedError extends SFTPError {}

export class SFTP {
    private client: Client;
    private sftp: SFTPWrapper | null = null;
    private connected: boolean = false;
    private sessionError: Error | null = null;
    private credentials: Credentials;

    constructor({ host, port, username, password }: Credentials) {
        this.client = new Client();

        this.credentials = {
            host,
            port,
            username,
            password,
        };
    }

    async connect(): Promise<void> {
        if (this.connected) {
            throw new SFTPConnectionError("Already connected");
        }

        this.sessionError = null;

        await new Promise<void>((resolve, reject) => {
            const cleanup = () => {
                this.client.off("ready", onReady);
                this.client.off("error", onError);
            };

            const onReady = () => {
                cleanup();
                resolve();
            };

            const onError = (error: Error) => {
                cleanup();
                reject(
                    new SFTPConnectionError(
                        `Failed to connect to ${this.credentials.host}:${this.credentials.port}`,
                        { cause: error },
                    ),
                );
            };

            this.client.once("ready", onReady).once("error", onError);
            this.client.connect(this.credentials);
        });

        // Erros após o handshake viram exceção não tratada do processo se ninguém
        // escutar 'error'; guardamos o último para reportar na próxima operação.
        this.client.on("error", (error: Error) => {
            this.sessionError = error;
            this.connected = false;
            this.sftp = null;
        });

        this.sftp = await promisify(this.client.sftp.bind(this.client))();
        this.connected = true;
    }

    async disconnect(): Promise<void> {
        if (!this.connected) {
            return;
        }

        await new Promise<void>((resolve) => {
            this.client.once("close", () => resolve());
            this.client.end();
        });

        this.connected = false;
        this.sftp = null;
    }

    async upload(source: string, remote: string): Promise<void> {
        const sftp = this.requireSftp();

        await pipeline(fs.createReadStream(source), sftp.createWriteStream(remote));
    }

    async download(remote: string, destination: string): Promise<void> {
        const sftp = this.requireSftp();

        await pipeline(sftp.createReadStream(remote), fs.createWriteStream(destination));
    }

    async listFiles(remoteDir: string): Promise<string[]> {
        const sftp = this.requireSftp();

        const entries = await promisify(sftp.readdir.bind(sftp))(remoteDir);

        return entries.map((entry) => entry.filename);
    }

    private requireSftp(): SFTPWrapper {
        if (this.sessionError) {
            throw new SFTPNotConnectedError("SFTP session was closed by an error", {
                cause: this.sessionError,
            });
        }

        if (!this.sftp) {
            throw new SFTPNotConnectedError("SFTP client not connected");
        }

        return this.sftp;
    }
}
