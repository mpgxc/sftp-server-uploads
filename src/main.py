from sftp import SFTPClient

if __name__ == "__main__":
    client = SFTPClient(
        hostname="127.0.0.1", port=2222, username="mpgxc", password="mpgxc_12345"
    )

    client.connect()
    client.listdir("/home/mpgxc/uploads")
    client.upload(
        "/home/mpgxc/mpgxc/sftp/.editorconfig", "/home/mpgxc/uploads/.editorconfig"
    )
    client.listdir("/home/mpgxc/uploads")

    # Exemplo de uso: client.download("/remote/path/file.txt", "/path/to/local/file.txt")

    client.disconnect()
