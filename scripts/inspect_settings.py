import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def inspect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'SELECT name FROM settings;'"
    stdin, stdout, stderr = client.exec_command(cmd)
    names = stdout.read().decode().strip().split('\n')
    print("Available setting names:", names)
    
    client.close()

if __name__ == "__main__":
    inspect()
