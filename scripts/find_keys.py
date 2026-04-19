import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def find_keys():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'SELECT key FROM settings;'"
    stdin, stdout, stderr = client.exec_command(cmd)
    keys = stdout.read().decode().strip().split('\n')
    
    print("Found keys:")
    for k in keys:
        if 'xray' in k.lower() or 'routing' in k.lower() or 'dns' in k.lower():
            print(f" - {k}")
            
    client.close()

if __name__ == "__main__":
    find_keys()
