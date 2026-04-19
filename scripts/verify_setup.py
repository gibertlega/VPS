import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def verify():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'SELECT name, value FROM settings WHERE name IN (\"xray_routing\", \"xray_dns\");'"
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode()
    
    print("--- ТЕКУЩИЕ НАСТРОЙКИ НА СЕРВЕРЕ ---")
    if "outboundTag" in output and "77.88.8.8" in output:
        print("✅ Настройки успешно применены!")
        print(output)
    else:
        print("❌ Настройки НЕ найдены или применились неверно.")
        print("Вывод БД:", output)
        
    client.close()

if __name__ == "__main__":
    verify()
