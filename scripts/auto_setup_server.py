import paramiko
import json

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

# Правила маршрутизации (Routing)
ROUTING_JSON = {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
        {"type": "field", "outboundTag": "block", "protocol": ["bittorrent"]},
        {"type": "field", "outboundTag": "block", "port": "25,465,587"},
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
        },
        {"type": "field", "outboundTag": "proxy", "network": "tcp,udp"}
    ]
}

# Настройки DNS
DNS_JSON = {
    "servers": [
        "1.1.1.1",
        {
            "address": "77.88.8.8",
            "port": 53,
            "domains": ["geosite:ru", "regexp:.*\\.ru$", "regexp:.*\\.su$"],
            "expectIPs": ["geoip:ru"]
        }
    ]
}

def apply_config():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    print("--- 1. Обновление Geo-баз и ру-блоклиста ---")
    commands = [
        "wget -O /usr/local/share/xray/geosite.dat https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat",
        "wget -O /usr/local/share/xray/geoip.dat https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat",
        "wget -O /usr/local/share/xray/ru-blocklist-extended-domain.dat https://github.com/UnRKN/ru-blocklist/releases/latest/download/ru-blocklist-extended-domain.dat",
        # Копируем в папку бинарника на всякий случай
        "cp /usr/local/share/xray/*.dat /usr/local/x-ui/bin/"
    ]
    for cmd in commands:
        print(f"Выполняю: {cmd}")
        client.exec_command(cmd)
        
    print("\n--- 2. Инъекция настроек в базу 3X-UI ---")
    # Кодируем JSON в строки для SQL
    routing_str = json.dumps(ROUTING_JSON)
    dns_str = json.dumps(DNS_JSON)
    
    # SQL команды для обновления
    sql_cmds = [
        f"sqlite3 /etc/x-ui/x-ui.db \"UPDATE settings SET value = '{routing_str}' WHERE name = 'xray_routing';\"",
        f"sqlite3 /etc/x-ui/x-ui.db \"UPDATE settings SET value = '{dns_str}' WHERE name = 'xray_dns';\""
    ]
    
    for sql in sql_cmds:
        client.exec_command(sql)
        
    print("\n--- 3. Перезапуск X-UI для применения настроек ---")
    client.exec_command("x-ui restart")
    
    print("\n✅ Всё готово! Сервер настроен.")
    client.close()

if __name__ == "__main__":
    apply_config()
