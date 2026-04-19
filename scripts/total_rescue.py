import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Самый безопасный и полный конфиг, восстанавливающий панель
SAFE_FULL_CONFIG = {
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
        "domainStrategy": "AsIs", 
        "rules": [
            {"type": "field", "outboundTag": "direct", "domain": ["regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$"]},
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"},
            {"type": "field", "outboundTag": "blocked", "protocol": ["bittorrent"]}
        ]
    }
}

def final_rescue():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    config_json = json.dumps(SAFE_FULL_CONFIG)
    sql_safe = config_json.replace("'", "''")
    
    # Записываем в файл для надежности
    with open("rescue.sql", "w") as f:
        f.write(f"UPDATE settings SET value = '{sql_safe}' WHERE key = 'xrayTemplateConfig';\n")
        
    sftp = client.open_sftp()
    sftp.put("rescue.sql", "/tmp/rescue.sql")
    sftp.close()
    
    print("Применяю спасательный конфиг...")
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/rescue.sql")
    
    print("Принудительный рестарт x-ui...")
    client.exec_command("x-ui restart")
    
    os.remove("rescue.sql")
    print("Done. Clean Log.")
    client.close()

if __name__ == "__main__":
    final_rescue()
