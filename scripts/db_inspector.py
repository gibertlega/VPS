import paramiko
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def inspect_db():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    # Запрос настроек
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'SELECT name, value FROM settings;'"
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode()
    
    print("--- 3X-UI SETTINGS ---")
    print(output)
    
    client.close()

if __name__ == "__main__":
    inspect_db()
