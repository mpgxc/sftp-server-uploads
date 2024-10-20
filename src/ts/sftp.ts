import fs from "node:fs";
import { pipeline } from "node:stream/promises";
import { promisify } from "node:util";
import { Client, SFTPWrapper } from "ssh2";

type Credentials = {
    host: string;
    port: number;
    username: string;
    password: string;
};

class SFTP {
    private client: Client;
    private sftp: SFTPWrapper | null = null;
    private connected: boolean = false;
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
            throw new Error("Already connected");
        }

        await new Promise<void>((resolve, reject) => {
            this.client
                .on("ready", resolve)
                .on("error", reject)
                .connect(this.credentials);
        });

        this.sftp = await promisify(this.client.sftp).bind(this.client)();
        this.connected = true;
    }

    disconnect(): void {
        if (this.connected) {
            this.client.end();
            this.connected = false;
        }
    }

    async upload(source: string, remote: string): Promise<void> {
        if (!this.sftp) {
            throw new Error("SFTP client not connected");
        }

        const from = fs.createReadStream(source);

        const destination = this.sftp.createWriteStream(remote);

        await pipeline(from, destination);
    }

    async listFiles(remoteDir: string): Promise<string[]> {
        if (!this.sftp) {
            return Promise.reject(new Error("SFTP client not connected"));
        }

        return new Promise((resolve, reject) => {
            this.sftp!.readdir(remoteDir, (err, fileList) => {
                if (err) {
                    return reject(err);
                }

                resolve(fileList.map((file) => file.filename));
            });
        });
    }
}

const sftp = new SFTP({
    host: "localhost",
    port: 2222,
    username: "mpgxc_docker",
    password: "mpgxc_docker",
});

(async () => {
    try {
        await sftp.connect();

        const files = await sftp.listFiles("/folder/sub_folder");

        console.info(JSON.stringify(files, null, 2));

        await sftp.upload("./data.txt", "/folder/sub_folder/file_name.csv");
    } catch (err) {
        console.error("Erro:", err);
    } finally {
        sftp.disconnect();
    }
})();
