import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Итоговый ПРАВИЛЬНЫЙ конфиг
FINAL_CONFIG = {
    "log": {"access": "none", "dnsLog": False, "error": "", "loglevel": "warning"},
    "dns": {
        "servers": [
            "1.1.1.1",
            {
                "address": "77.88.8.8",
                "port": 53,
                "domains": ["geosite:ru", "regexp:.*\\.ru$", "regexp:.*\\.su$"],
                "expectIPs": ["geoip:ru"]
            }
        ]
    },
    "routing": {
        "domainStrategy": "IPIfNonMatch",
        "rules": [
            {"type": "field", "outboundTag": "block", "protocol": ["bittorrent"]},
            {
                "type": "field",
                "outboundTag": "direct",
                "domain": ["geosite:ru", "geosite:category-gov-ru", "regexp:.*\\.ru$", "regexp:.*\\.su$"],
                "ip": ["geoip:ru", "geoip:private"]
            },
            {
                "type": "field",
                "outboundTag": "proxy",
                "domain": ["ext:ru-blocklist-extended-domain.dat:all", "geosite:google", "geosite:youtube", "geosite:telegram"]
            }
        ]
    }
}

def deploy_fix():
    print("Создаю SQL файл локально...")
    config_str = json.dumps(FINAL_CONFIG)
    # Экранируем одинарные кавычки для SQL
    sql_safe_config = config_str.replace("'", "''")
    sql_content = f"UPDATE settings SET value = '{sql_safe_config}' WHERE key = 'xrayTemplateConfig';\n"
    
    with open("fix.sql", "w") as f:
        f.write(sql_content)

    print("Подключаюсь к серверу...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    print("Загружаю SQL файл на сервер...")
    sftp = client.open_sftp()
    sftp.put("fix.sql", "/tmp/fix.sql")
    sftp.close()
    
    print("Применяю фикс в БД...")
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/fix.sql")
    
    print("Перезапускаю X-UI...")
    client.exec_command("x-ui restart")
    
    print("Удаляю временные файлы...")
    client.exec_command("rm /tmp/fix.sql")
    os.remove("fix.sql")
    
    print("✅ ГОТОВО! ВПН должен ожить.")
    client.close()

if __name__ == "__main__":
    deploy_fix()
