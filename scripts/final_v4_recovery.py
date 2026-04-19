import paramiko
import json
import os

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Упрощенный, неубиваемый конфиг
FINAL_CONFIG = {
    "log": {"access": "none", "dnsLog": False, "error": "", "loglevel": "warning"},
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
            {"type": "field", "inboundTag": ["api"], "outboundTag": "api"}
        ]
    }
}

def deploy_v4():
    print("Подключаюсь к серверу...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    print("Скачиваю официальные базы v2fly (где 100% есть RU)...")
    commands = [
        "wget -O /usr/local/share/xray/geosite.dat https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat",
        "wget -O /usr/local/share/xray/geoip.dat https://github.com/v2fly/geoip/releases/latest/download/geoip.dat",
        "cp /usr/local/share/xray/*.dat /usr/local/x-ui/bin/"
    ]
    for cmd in commands:
        client.exec_command(cmd)

    print("Создаю SQL фикс...")
    config_str = json.dumps(FINAL_CONFIG)
    sql_safe_config = config_str.replace("'", "''")
    sql_content = f"UPDATE settings SET value = '{sql_safe_config}' WHERE key = 'xrayTemplateConfig';\n"
    
    with open("fix_v4.sql", "w") as f:
        f.write(sql_content)

    sftp = client.open_sftp()
    sftp.put("fix_v4.sql", "/tmp/fix_v4.sql")
    sftp.close()
    
    print("Применяю фикс в БД...")
    client.exec_command("sqlite3 /etc/x-ui/x-ui.db < /tmp/fix_v4.sql")
    
    print("Перезапускаю X-UI...")
    client.exec_command("x-ui restart")
    
    print("Очистка...")
    client.exec_command("rm /tmp/fix_v4.sql")
    os.remove("fix_v4.sql")
    
    print("Mission Complete (v4). Check VPN.")
    client.close()

if __name__ == "__main__":
    deploy_v4()
