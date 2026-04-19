import paramiko
import time
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

print("Подключаюсь к серверу для установки AmneziaWG...")
try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=10)
    sftp = client.open_sftp()
except Exception as e:
    print("Ошибка SSH:", e)
    exit()

# Читаем баш-скрипт с диска
with open("e:\\VPS\\scripts\\setup_awg_secure.sh", "r", encoding="utf-8") as f:
    sh_content = f.read()

# Записываем на сервер
with sftp.file("/root/setup_awg.sh", "w") as f:
    f.write(sh_content.replace('\r\n', '\n'))
sftp.close()

# Запускаем в бэкграунде (nohup), чтобы избежать зависаний paramiko
print("Запускаю скрипт установки на сервере (это займет около 1-2 минут)...")
client.exec_command("chmod +x /root/setup_awg.sh")
client.exec_command("rm -f /root/awg_install.log")
client.exec_command("nohup /root/setup_awg.sh > /root/awg_install.log 2>&1 &")

# Проверяем лог, пока не появится слово ГОТОВО (====)
success = False
for i in range(25):
    time.sleep(5)
    _, stdout, _ = client.exec_command("tail -n 35 /root/awg_install.log")
    log = stdout.read().decode('utf-8', errors='ignore')
    if "УСТАНОВЛЕН И ЗАЩИЩЕН" in log:
        print("\n" + "="*50)
        print(log[log.find("УСТАНОВЛЕН И ЗАЩИЩЕН")-30:])
        success = True
        break
    else:
        print(".", end="", flush=True)

if not success:
    print("\n[!] Установка идет дольше обычного, проверьте лог на сервере: cat /root/awg_install.log")

client.close()
print("\nПроцесс завершен.")
