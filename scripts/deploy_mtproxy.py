import paramiko
import secrets
import time

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"
PORT_MTG = 8888

# Генерируем случайный 16-байтный секрет
SECRET_HEX = secrets.token_hex(16)
# Для режима DD (лучше скрывает трафик) добавляем префикс dd
SECRET_DD = "dd" + SECRET_HEX

def run(client, cmd, timeout=30):
    print(f"\n>>> {cmd}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print("OUT:", out)
    if err and "warning" not in err.lower(): print("ERR:", err)
    return out

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Подключаюсь к {HOST}...")
client.connect(HOST, username=USER, password=PASS, timeout=15)
print("Подключен!\n")

# --- ШАГ 1: Клонируем mtprotoproxy ---
print("=== ШАГ 1: Устанавливаем mtprotoproxy ===")
run(client, "apt-get install -y git > /dev/null 2>&1 && echo 'git OK'")

# Проверяем, не установлен ли уже
check = run(client, "test -d /opt/mtprotoproxy && echo 'exists' || echo 'not found'")
if 'not found' in check:
    run(client, "git clone https://github.com/alexbers/mtprotoproxy.git /opt/mtprotoproxy")
    print("Репозиторий склонирован.")
else:
    print("mtprotoproxy уже установлен, обновляем...")
    run(client, "git -C /opt/mtprotoproxy pull")

# --- ШАГ 2: Создаём конфиг ---
print(f"\n=== ШАГ 2: Создаём конфиг (порт {PORT_MTG}, секрет: {SECRET_HEX}) ===")
config_content = f"""# MTProxy Config
PORT = {PORT_MTG}
USERS = {{
    "tg_user": "{SECRET_HEX}"
}}
# Режим DD - лучше обходит блокировки
USE_MIDDLE_PROXY = False
"""
sftp = client.open_sftp()
with sftp.open('/opt/mtprotoproxy/config.py', 'w') as f:
    f.write(config_content)
sftp.close()
print("Конфиг записан!")

# --- ШАГ 3: Создаём systemd сервис ---
print("\n=== ШАГ 3: Регистрируем системный сервис ===")
service_content = """[Unit]
Description=MTProto Proxy for Telegram
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/mtprotoproxy
ExecStart=/usr/bin/python3 /opt/mtprotoproxy/mtprotoproxy.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""
sftp = client.open_sftp()
with sftp.open('/etc/systemd/system/mtprotoproxy.service', 'w') as f:
    f.write(service_content)
sftp.close()
print("Сервис зарегистрирован!")

# --- ШАГ 4: Запускаем ---
print("\n=== ШАГ 4: Запускаем сервис ===")
run(client, "systemctl daemon-reload")
run(client, "systemctl enable mtprotoproxy")
run(client, "systemctl restart mtprotoproxy")
time.sleep(3)  # Ждём запуска

# --- ШАГ 5: Проверка ---
print("\n=== ШАГ 5: Проверка статуса ===")
status = run(client, "systemctl is-active mtprotoproxy")

if "active" in status:
    print("\n✅ MTProxy ЗАПУЩЕН!")
    # Проверяем открытый порт
    run(client, f"ss -tlnp | grep {PORT_MTG}")
else:
    print("\n❌ Что-то пошло не так. Смотрим логи:")
    run(client, "journalctl -u mtprotoproxy -n 20 --no-pager")

client.close()

# --- ИТОГОВЫЕ ССЫЛКИ ---
print("\n" + "="*60)
print("🎉 ССЫЛКИ ДЛЯ TELEGRAM:")
print("="*60)
print(f"\n🔑 Секрет (простой):   {SECRET_HEX}")
print(f"🔑 Секрет (DD режим):  {SECRET_DD}")
print(f"\n📱 Ссылка для добавления в Telegram (нажми или отправь себе):")
print(f"https://t.me/proxy?server={HOST}&port={PORT_MTG}&secret={SECRET_DD}")
print(f"\n🔗 Ссылка tg:// (альтернативная):")
print(f"tg://proxy?server={HOST}&port={PORT_MTG}&secret={SECRET_DD}")
print("="*60)
