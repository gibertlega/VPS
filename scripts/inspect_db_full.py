import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def inspect_schema():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'PRAGMA table_info(settings);'"
    stdin, stdout, stderr = client.exec_command(cmd)
    print("Settings Schema:", stdout.read().decode())
    
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'SELECT * FROM settings LIMIT 5;'"
    stdin, stdout, stderr = client.exec_command(cmd)
    print("Settings Samples:", stdout.read().decode())
    
    client.close()

if __name__ == "__main__":
    inspect_schema()
