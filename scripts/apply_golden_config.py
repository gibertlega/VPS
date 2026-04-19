import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Идеальный конфиг со всеми плюшками
GOLDEN_CONFIG = {
    "log": {"access": "none", "dnsLog": False, "error": "", "loglevel": "warning", "maskAddress": ""}, 
    "api": {"tag": "api", "services": ["HandlerService", "LoggerService", "StatsService"]}, 
    "dns": {
        "servers": [
            "1.1.1.1",
            {
                "address": "77.88.8.8",
                "port": 53,
                "domains": ["geosite:ru", "regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$"],
                "expectIPs": ["geoip:ru"]
            }
        ]
    },
    "inbounds": [{"tag": "api", "listen": "127.0.0.1", "port": 62789, "protocol": "tunnel", "settings": {"address": "127.0.0.1"}}], 
    "outbounds": [
        {"tag": "proxy", "protocol": "freedom", "settings": {}}, # Заглушка, 3X-UI сам подставит нужное
        {"tag": "direct", "protocol": "freedom", "settings": {"domainStrategy": "UseIP"}}, 
        {"tag": "blocked", "protocol": "blackhole", "settings": {}}
    ], 
    "policy": {
        "levels": {"0": {"statsUserDownlink": True, "statsUserUplink": True}}, 
        "system": {"statsInboundDownlink": True, "statsInboundUplink": True}
    }, 
    "routing": {
        "domainStrategy": "IPIfNonMatch", 
        "rules": [
            {"type": "field", "outboundTag": "blocked", "protocol": ["bittorrent"]},
            # 1. RU Трафик -> Напрямую
            {
                "type": "field", 
                "outboundTag": "direct", 
                "domain": ["geosite:ru", "geosite:category-gov-ru", "regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$"],
                "ip": ["geoip:ru", "geoip:private"]
            },
            # 2. Список блокировок РКН -> Через Прокси
            {
                "type": "field", 
                "outboundTag": "proxy", 
                "domain": ["ext:ru-blocklist-extended-domain.dat:all"]
            },
            # 3. Сервисы AI и Google -> Через Прокси
            {
                "type": "field", 
                "outboundTag": "proxy", 
                "domain": ["geosite:google", "geosite:openai", "geosite:youtube", "geosite:telegram", "geosite:netflix"]
            },
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"}
        ]
    }
}

def apply_golden():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    config_json = json.dumps(GOLDEN_CONFIG)
    sql_safe = config_json.replace("'", "''")
    
    with open("golden.sql", "w") as f:
        f.write(f"UPDATE settings SET value = '{sql_safe}' WHERE key = 'xrayTemplateConfig';\n")
        
    sftp = client.open_sftp()
    sftp.put("golden.sql", "/tmp/golden.sql")
    sftp.close()
    
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/golden.sql")
    client.exec_command("pkill -9 xray; x-ui restart")
    
    os.remove("golden.sql")
    print("Golden Config applied successfully.")
    client.close()

if __name__ == "__main__":
    apply_golden()
