import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# САМЫЙ простой конфиг БЕЗ geosite/geoip (чтобы точно завелось)
FINAL_CONFIG = {
    "log": {"access": "none", "dnsLog": False, "error": "", "loglevel": "warning"},
    "routing": {
        "domainStrategy": "AsIs",
        "rules": [
            {
                "type": "field",
                "outboundTag": "direct",
                "domain": ["regexp:.*\\.ru$", "regexp:.*\\.su$", "regexp:.*\\.xn--p1ai$"]
            },
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"}
        ]
    }
}

def deploy_v5():
    print("Подключаюсь к серверу...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    print("Создаю SQL фикс (режим 'No-Geo')...")
    config_str = json.dumps(FINAL_CONFIG)
    sql_safe_config = config_str.replace("'", "''")
    sql_content = f"UPDATE settings SET value = '{sql_safe_config}' WHERE key = 'xrayTemplateConfig';\n"
    
    with open("fix_v5.sql", "w") as f:
        f.write(sql_content)

    sftp = client.open_sftp()
    sftp.put("fix_v5.sql", "/tmp/fix_v5.sql")
    sftp.close()
    
    print("Применяю фикс в БД...")
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/fix_v5.sql")
    
    print("Перезапускаю X-UI...")
    client.exec_command("x-ui restart")
    
    print("✅ V5 Deployed. Xray SHOULD start now.")
    client.close()

if __name__ == "__main__":
    deploy_v5()
