import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def fetch():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    for key in ['xrayTemplateConfig', 'subRoutingRules']:
        print(f"\n--- {key} ---")
        cmd = f"sqlite3 /etc/x-ui/x-ui.db 'SELECT value FROM settings WHERE key = \"{key}\";'"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        
    client.close()

if __name__ == "__main__":
    fetch()
