import os
import time
import requests
import paramiko
import psutil # Note: psutil will be used for local monitoring if run on VPS
from datetime import datetime

# Script to deploy vps_monitor on the VPS remotely via paramiko

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# The python code that will actually run ON THE VPS
REMOTE_SCRIPT = """#!/usr/bin/env python3
import time
import subprocess
import urllib.request
import urllib.parse
import json

TOKEN = "8763168285:AAHb-2-a5HziTC-hCwng3wvZBQumOsVsLZc"
CHAT_ID = "412025563"
CHECK_INTERVAL = 3600 # 1 час

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print("Failed to send alert", e)

def check_resources():
    # CPU usage
    cpu_idle = float(subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $8}'", shell=True).decode().strip())
    cpu_usage = 100.0 - cpu_idle

    # RAM usage
    mem_total = float(subprocess.check_output("free | grep Mem | awk '{print $2}'", shell=True))
    mem_used = float(subprocess.check_output("free | grep Mem | awk '{print $3}'", shell=True))
    mem_usage = (mem_used / mem_total) * 100

    # Disk usage
    disk_usage = float(subprocess.check_output("df / | tail -1 | awk '{print $5}' | sed 's/%//'", shell=True))

    alerts = []
    if cpu_usage > 90:
        alerts.append(f"🔥 ВНИМАНИЕ: Высокая нагрузка CPU — {cpu_usage:.1f}%")
    if mem_usage > 90:
        alerts.append(f"🔥 ВНИМАНИЕ: Заканчивается ОЗУ — {mem_usage:.1f}% занято")
    if disk_usage > 90:
        alerts.append(f"🔥 ВНИМАНИЕ: Заканчивается место на диске — {disk_usage:.1f}%")

    if alerts:
        send_alert("\\n".join(alerts))

if __name__ == "__main__":
    send_alert("✅ Система мониторинга ресурсов сервера успешно запущена!")
    while True:
        try:
            check_resources()
        except Exception as e:
            print("Monitoring error:", e)
        time.sleep(CHECK_INTERVAL)
"""

SERVICE_FILE = """[Unit]
Description=Lega VPS Monitoring Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /opt/vps_monitor/monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
"""

print("Подключаюсь к серверу для установки мониторинга...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)
sftp = client.open_sftp()

def run(cmd):
    client.exec_command(cmd)

run("mkdir -p /opt/vps_monitor")

# Создаем скрипт мониторинга
with sftp.file("/opt/vps_monitor/monitor.py", "w") as f:
    f.write(REMOTE_SCRIPT)
run("chmod +x /opt/vps_monitor/monitor.py")

# Создаем файл сервиса
with sftp.file("/etc/systemd/system/vps_monitor.service", "w") as f:
    f.write(SERVICE_FILE)

# Запускаем службу
run("systemctl daemon-reload")
run("systemctl enable vps_monitor.service")
run("systemctl restart vps_monitor.service")

print("✅ Служба мониторинга успешно установлена и запущена на сервере!")
sftp.close()
client.close()
