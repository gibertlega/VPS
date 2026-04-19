import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Оригинальный полный конфиг Олега (с исправленными правилами)
RECOVERY_CONFIG = {
    "log": {"access": "none", "dnsLog": False, "error": "", "loglevel": "warning", "maskAddress": ""}, 
    "api": {"tag": "api", "services": ["HandlerService", "LoggerService", "StatsService"]}, 
    "inbounds": [{"tag": "api", "listen": "127.0.0.1", "port": 62789, "protocol": "tunnel", "settings": {"address": "127.0.0.1"}}], 
    "outbounds": [
        {"tag": "direct", "protocol": "freedom", "settings": {"domainStrategy": "AsIs", "redirect": "", "noises": []}}, 
        {"tag": "blocked", "protocol": "blackhole", "settings": {}}
    ], 
    "policy": {
        "levels": {"0": {"statsUserDownlink": True, "statsUserUplink": True}}, 
        "system": {"statsInboundDownlink": True, "statsInboundUplink": True}
    }, 
    "routing": {
        "domainStrategy": "IPIfNonMatch", 
        "rules": [
            # Правило 1: Только домены .ru / .su / госуслуги -> Direct
            {"type": "field", "outboundTag": "direct", "domain": ["regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$"]},
            # Правило 2: Внутренние API панели -> api
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"},
            # Правило 3: Приватные сети и торренты -> Blocked
            {"type": "field", "outboundTag": "blocked", "ip": ["geoip:private"], "protocol": ["bittorrent"]}
        ]
    }
}

def restore_full():
    print("Подключаюсь...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    config_json = json.dumps(RECOVERY_CONFIG)
    sql_safe = config_json.replace("'", "''")
    
    with open("restore.sql", "w") as f:
        f.write(f"UPDATE settings SET value = '{sql_safe}' WHERE key = 'xrayTemplateConfig';\n")
        
    sftp = client.open_sftp()
    sftp.put("restore.sql", "/tmp/restore.sql")
    sftp.close()
    
    print("Применяю полную структуру...")
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/restore.sql")
    
    print("Рестарт x-ui...")
    client.exec_command("x-ui restart")
    
    os.remove("restore.sql")
    print("✅ RESTORED. Проверяй панель и ВПН.")
    client.close()

if __name__ == "__main__":
    restore_full()
