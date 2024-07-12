from sftp import SFTPClient

if __name__ == "__main__":
    client = SFTPClient(
        hostname="127.0.0.1",
        port=2222,
        username="mpgxc",
        password="mpgxc_12345"
    )

    client.connect().unwrap()

    client.listdir("/home/mpgxc/uploads").unwrap()
    client.upload(
        "/home/mpgxc/Lab/sftp-server-uploads/src/file.txt", "/home/mpgxc/uploads/.editorconfig"
    ).unwrap()
    client.listdir("/home/mpgxc/uploads").unwrap()

    # Exemplo de uso: client.download("/remote/path/file.txt", "/path/to/local/file.txt").unwrap()

    client.disconnect().unwrap()
