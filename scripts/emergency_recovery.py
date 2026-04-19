import paramiko
import json

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

def recovery():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    print("--- Чтение текущего шаблона ---")
    cmd = "sqlite3 /etc/x-ui/x-ui.db \"SELECT value FROM settings WHERE key = 'xrayTemplateConfig';\""
    stdin, stdout, stderr = client.exec_command(cmd)
    raw_config = stdout.read().decode().strip()
    
    if not raw_config:
        print("Ошибка: Шаблон не найден!")
        return

    config = json.loads(raw_config)
    
    # 1. Исправляем routing.rules
    # Удаляем битый тег или заменяем его
    rules = config.get("routing", {}).get("rules", [])
    new_rules = []
    for rule in rules:
        # Если в доменах есть битый тег, исправляем его
        if "domain" in rule:
            rule["domain"] = [d.replace(":RU", ":all") for d in rule["domain"]]
        new_rules.append(rule)
    
    config["routing"]["rules"] = new_rules
    config["routing"]["domainStrategy"] = "IPIfNonMatch"
    
    # 2. Добавляем блокировку рекламы и трекеров (бонус)
    config["routing"]["rules"].insert(0, {
        "type": "field",
        "domain": ["geosite:category-ads-all"],
        "outboundTag": "blocked"
    })

    new_config_str = json.dumps(config)
    
    print("--- Сохранение исправленного шаблона ---")
    # Экранируем двойные кавычки для SQL
    sql_safe_config = new_config_str.replace("'", "''")
    update_cmd = f"sqlite3 /etc/x-ui/x-ui.db \"UPDATE settings SET value = '{sql_safe_config}' WHERE key = 'xrayTemplateConfig';\""
    client.exec_command(update_cmd)
    
    print("--- Рестарт сервера ---")
    client.exec_command("x-ui restart")
    
    print("✅ Восстановление завершено! Проверяй.")
    client.close()

if __name__ == "__main__":
    recovery()
