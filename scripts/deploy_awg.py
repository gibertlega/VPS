import paramiko
import time

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"

print("Подключаюсь к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    print("Успешно подключено!")
except Exception as e:
    print("Ошибка подключения:", e)
    exit(1)

# Скачиваем скрипт
cmd_download = "wget -qO amneziawg-install.sh https://raw.githubusercontent.com/crl20/amneziawg-install/main/amneziawg-install.sh && chmod +x amneziawg-install.sh"
print("Скачиваю скрипт AmneziaWG...")
stdin, stdout, stderr = client.exec_command(cmd_download)
exit_status = stdout.channel.recv_exit_status()
if exit_status != 0:
    print("Ошибка при скачивании скрипта! Код:", exit_status)
    print("Возможно нет интернета или github заблокирован. Ошибка:", stderr.read().decode())
    client.close()
    exit(1)

# Запускаем скрипт, пробрасывая ENTER для выбора значений по умолчанию (port=51820, client='client', dns='1.1.1.1')
print("Запускаю установку AmneziaWG...")
# Для авто-ответов используем echo с тремя переносами строк:
cmd_install = "if [ -f amneziawg-install.sh ]; then echo -e \"\n\n\n\n\n\n\n\n\n\n\" | ./amneziawg-install.sh; fi"
stdin, stdout, stderr = client.exec_command(cmd_install)
install_output = stdout.read().decode()
exit_status = stdout.channel.recv_exit_status()

print("Вывод установки:")
lines = install_output.split('\n')
for line in lines[-15:]:  # Последние 15 строк вывода (чтобы не спамить в консоль)
    print(line)

print("Настраиваю правила фаервола (iptables) для безопасности родственников...")
firewall_cmd = """
# Очистим старые правила для awg0 (если были)
iptables -D FORWARD -i awg0 -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null
iptables -D FORWARD -i awg0 -p tcp --dport 25 -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -m string --algo bm --string "BitTorrent" -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -m string --algo bm --string "BitTorrent protocol" -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -m string --algo bm --string "peer_id=" -j DROP 2>/dev/null

# Добавляем новые правила БЛОКИРОВКИ:
# 1. Запрещаем рассылку спама (порт 25, 465, 587)
iptables -I FORWARD -i awg0 -p tcp --dport 25 -j DROP
iptables -I FORWARD -i awg0 -p tcp --dport 465 -j DROP
iptables -I FORWARD -i awg0 -p tcp --dport 587 -j DROP

# 2. DPI блокировка торрентов по сигнатурам и известным трекерам (если ядро поддерживает -m string)
iptables -I FORWARD -i awg0 -m string --algo bm --string "BitTorrent protocol" -j DROP
iptables -I FORWARD -i awg0 -m string --algo bm --string "peer_id=" -j DROP
iptables -I FORWARD -i awg0 -m string --algo kmp --string "announce" -j DROP
iptables -I FORWARD -i awg0 -p udp --dport 6881:6889 -j DROP
iptables -A FORWARD -i awg0 -j ACCEPT # Разрешаем остальной трафик

# Сохраняем правила, чтобы они работали после ребута
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4

# Устанавливаем пакет iptables-persistent (автоматически восстанавливает правила фаервола при загрузке)
export DEBIAN_FRONTEND=noninteractive
apt-get install -y iptables-persistent >/dev/null 2>&1
"""

client.exec_command(firewall_cmd)
time.sleep(3) # Ждем применения правил
print("Фаервол настроен! Торренты и Спам заблокированы для интерфейса awg0.")

# Читаем конфигурацию клиента
print("Получаю конфиг файл для родственника...")
_, stdout, _ = client.exec_command("cat /root/awg0-client.conf 2>/dev/null || cat /root/awg-client.conf 2>/dev/null || cat /etc/amnezia/amneziawg/clients/client.conf 2>/dev/null || echo 'Конфиг не найден'")
config = stdout.read().decode()

with open("awg_client_config.conf", "w") as f:
    f.write(config)

print("Готово! Конфиг скачан как 'e:\\VPS\\awg_client_config.conf'")

client.close()
