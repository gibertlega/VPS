import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# САМЫЙ надежный вариант: БЕЗ geosite:ru и geosite:google и прочего. Только regex.
BULLETPROOF_CONFIG = {
    "log": {"access": "none", "dnsLog": False, "error": "", "loglevel": "warning", "maskAddress": ""}, 
    "api": {"tag": "api", "services": ["HandlerService", "LoggerService", "StatsService"]}, 
    "dns": {
        "servers": [
            "1.1.1.1",
            {
                "address": "77.88.8.8",
                "port": 53,
                "domains": ["regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$", "regexp:.*\\.yandex\\.", "regexp:.*\\.vk\\.com$"]
            }
        ]
    },
    "inbounds": [{"tag": "api", "listen": "127.0.0.1", "port": 62789, "protocol": "tunnel", "settings": {"address": "127.0.0.1"}}], 
    "outbounds": [
        {"tag": "proxy", "protocol": "freedom", "settings": {}}, 
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
            # ВПЕРЕД! Только REGEX.
            {
                "type": "field", 
                "outboundTag": "direct", 
                "domain": ["regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$", "regexp:.*\\.yandex\\.", "regexp:.*\\.vk\\.com$", "regexp:.*\\.gosuslugi\\.ru$"]
            },
            {
                "type": "field",
                "outboundTag": "proxy",
                "domain": ["regexp:.*\\.google\\.com$", "regexp:.*\\.youtube\\.com$", "regexp:.*\\.instagram\\.com$", "regexp:.*\\.facebook\\.com$", "regexp:.*\\.openai\\.com$"]
            },
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"}
        ]
    }
}

def apply_bulletproof():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    config_json = json.dumps(BULLETPROOF_CONFIG)
    sql_safe = config_json.replace("'", "''")
    
    with open("bulletproof.sql", "w") as f:
        f.write(f"UPDATE settings SET value = '{sql_safe}' WHERE key = 'xrayTemplateConfig';\n")
        
    sftp = client.open_sftp()
    sftp.put("bulletproof.sql", "/tmp/bulletproof.sql")
    sftp.close()
    
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/bulletproof.sql")
    client.exec_command("pkill -9 xray; x-ui restart")
    
    os.remove("bulletproof.sql")
    client.close()

if __name__ == "__main__":
    apply_bulletproof()
