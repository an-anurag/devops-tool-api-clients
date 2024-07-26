import io
import paramiko


class SSHClient:
    def __init__(self, hostname, username, password, key_path=None):
        self.ssh = None
        self.sftp = None
        self.hostname = hostname
        self.port = 22
        self.username = username
        self.password = password
        self.private_key = key_path

    def connect_with_password(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.hostname, port=22, username=self.username, password=self.password)
        print(f"info: connected to {self.hostname} with password.")

    def connect_with_key(self, username):
        pkey = paramiko.RSAKey.from_private_key_file(self.private_key)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.hostname, port=22, username=username, pkey=pkey)
        print(f"info: connected to {self.hostname} with key.")

    def connect_sftp(self):
        self.sftp = self.ssh.open_sftp()

    def execute_command(self, command):
        """Execute a command on the remote server."""
        self.ssh.exec_command(command)
        stdout = self.ssh.makefile("rb", -1).read().decode("utf-8")
        stderr = self.ssh.makefile_stderr("rb", -1).read().decode("utf-8")

        if stdout:
            print(f"Command output:\n{stdout}")

        if stderr:
            print(f"Command error:\n{stderr}")

    def scp_string_to_remote(self, content, remote_path):
        """SCP a string content to the remote server."""
        try:
            # Create an in-memory file-like object
            f = io.BytesIO(content.encode())
            # Upload the in-memory file to remote server
            self.sftp.putfo(f, remote_path)
            print(f"info: string content uploaded to {remote_path} successfully.")
        except Exception as e:
            print(f"error: Error uploading string content: {e}")

    def scp_file_to_remote(self, local_path, remote_path):
        """SCP a file to the remote server."""
        try:
            self.sftp.put(local_path, remote_path)
            print(f"info: file {local_path} uploaded to {remote_path} successfully.")
        except Exception as e:
            print(f"error: error uploading file: {e}")

    def create_nested_directory(self, remote_dir_path):
        """Create nested directories on the remote server."""
        dirs = remote_dir_path.split('/')
        for i in range(1, len(dirs)):
            dir_path = '/'.join(dirs[:i + 1])
            try:
                self.sftp.stat(dir_path)
            except FileNotFoundError:
                self.sftp.mkdir(dir_path)
                print(f"info: directory {dir_path} created successfully.")
            except Exception as e:
                print(f"error: error creating directory {dir_path}: {e}")

    def disconnect(self):
        """Close the SSH connection."""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        print("info: disconnected from the remote server.")




if __name__ == '__main__':
    # Create an SSH client
    ssh_client = SSHClient(hostname='1.1.1.1', username='service-user', password='password')
    # ssh_client.connect_with_key('opc')
    ssh_client.connect_with_password()
    ssh_client.connect_sftp()
    ssh_client.create_nested_directory('/var/www/html/')
    ssh_client.scp_file_to_remote('changelog.log', '/var/www/html/changelog.log')
