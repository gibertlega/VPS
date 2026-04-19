"""
 Полный бэкап всех критических файлов VPS-сервера.
 Запускай этот скрипт, когда хочешь сохранить текущее состояние.
 Всё скачивается в e:/VPS/backup/
 """

import paramiko
import os
import datetime
import stat

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Папка для бэкапа с датой
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
BACKUP_DIR = f"e:/VPS/backup/{timestamp}"

# Список файлов и папок для бэкапа
BACKUP_TARGETS = [
    # 3X-UI Panel (самое важное - БД со всеми ключами)
    "/etc/x-ui/x-ui.db",
    # Xray конфиг
    "/usr/local/x-ui/bin/config.json",
    # Nginx
    "/etc/nginx/nginx.conf",
    "/etc/nginx/sites-enabled/",
    "/etc/nginx/sites-available/",
    # SSL сертификаты
    "/etc/letsencrypt/live/",
    "/etc/letsencrypt/renewal/",
    # Заглушка-сайт
    "/var/www/html/index.html",
    # MTProxy
    "/opt/mtprotoproxy/config.py",
    # Systemd сервисы (наши кастомные)
    "/etc/systemd/system/mtprotoproxy.service",
]

def download_recursive(sftp, remote_path, local_path):
    """Рекурсивно скачивает файлы/папки"""
    try:
        file_attr = sftp.stat(remote_path)
    except FileNotFoundError:
        print(f"  [!] NOT FOUND: {remote_path}")
        return 0

    if stat.S_ISDIR(file_attr.st_mode):
        os.makedirs(local_path, exist_ok=True)
        count = 0
        try:
            for item in sftp.listdir(remote_path):
                remote_item = f"{remote_path}/{item}" if not remote_path.endswith('/') else f"{remote_path}{item}"
                local_item = os.path.join(local_path, item)
                count += download_recursive(sftp, remote_item, local_item)
        except PermissionError:
            print(f"  [!] NO PERMISSION: {remote_path}")
        return count
    else:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            sftp.get(remote_path, local_path)
            size = os.path.getsize(local_path)
            print(f"  [OK] {remote_path} ({size} bytes)")
            return 1
        except Exception as e:
            print(f"  [ERR] {remote_path}: {e}")
            return 0

def run(client, cmd):
    _, stdout, stderr = client.exec_command(cmd, timeout=30)
    return stdout.read().decode().strip()

# === НАЧАЛО ===
print(f"{'='*60}")
print(f" GOLDEN STANDARD BACKUP")
print(f" Date: {timestamp}")
print(f" Folder: {BACKUP_DIR}")
print(f"{'='*60}\n")

os.makedirs(BACKUP_DIR, exist_ok=True)

# Подключение
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Подключаюсь к {HOST}...")
client.connect(HOST, username=USER, password=PASS, timeout=15)
print("Подключен!\n")

sftp = client.open_sftp()

# Скачиваем все файлы
total = 0
for target in BACKUP_TARGETS:
    print(f"\n[FILE] {target}")
    # Преобразуем серверный путь в локальный
    # /etc/nginx/nginx.conf -> backup/2025-.../etc/nginx/nginx.conf
    local_target = os.path.join(BACKUP_DIR, target.lstrip('/'))
    total += download_recursive(sftp, target.rstrip('/'), local_target)

# Дополнительно сохраняем список пакетов и crontab
print(f"\n[INFO] Additional server info...")
extras_dir = os.path.join(BACKUP_DIR, "_server_info")
os.makedirs(extras_dir, exist_ok=True)

# Список установленных пакетов
packages = run(client, "dpkg --get-selections | head -200")
with open(os.path.join(extras_dir, "packages.txt"), 'w', encoding='utf-8') as f:
    f.write(packages)
print(f"  [OK] Packages list")
total += 1

# Crontab
cron = run(client, "crontab -l 2>/dev/null || echo 'Нет crontab'")
with open(os.path.join(extras_dir, "crontab.txt"), 'w', encoding='utf-8') as f:
    f.write(cron)
print(f"  [OK] Crontab")
total += 1

# Статус сервисов
services = run(client, "systemctl list-units --type=service --state=running --no-pager")
with open(os.path.join(extras_dir, "services.txt"), 'w', encoding='utf-8') as f:
    f.write(services)
print(f"  [OK] Running services list")
total += 1

# Версии ключевого софта
versions = run(client, "echo '--- OS ---' && cat /etc/os-release && echo '--- Nginx ---' && nginx -v 2>&1 && echo '--- Python ---' && python3 --version && echo '--- Xray ---' && /usr/local/x-ui/bin/xray-linux-amd64 version 2>/dev/null || echo 'xray version N/A'")
with open(os.path.join(extras_dir, "versions.txt"), 'w', encoding='utf-8') as f:
    f.write(versions)
print(f"  [OK] Software versions")
total += 1

sftp.close()
client.close()

print(f"\n{'='*60}")
print(f" BACKUP COMPLETE!")
print(f" Total files: {total}")
print(f" Saved to: {BACKUP_DIR}")
print(f"{'='*60}")
