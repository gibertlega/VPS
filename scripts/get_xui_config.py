import paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def get_config():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    # Пытаемся взять данные через sqlite3
    # В 3X-UI настройки часто в таблице 'settings'
    cmd = "sqlite3 /etc/x-ui/x-ui.db 'SELECT name, value FROM settings WHERE name LIKE \"xray%\";'"
    stdin, stdout, stderr = client.exec_command(cmd)
    
    output = stdout.read().decode()
    if not output:
        print("Настройки не найдены в таблице 'settings'. Возможно другая версия панели.")
        # Проверим список таблиц
        stdin, stdout, stderr = client.exec_command("sqlite3 /etc/x-ui/x-ui.db '.tables'")
        print("Таблицы:", stdout.read().decode())
    else:
        print(output)
        
    client.close()

if __name__ == "__main__":
    get_config()
