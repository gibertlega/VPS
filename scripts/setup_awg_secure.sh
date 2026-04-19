#!/bin/bash
# Запуск от имени root (sudo)

echo "=============== УСТАНОВКА AMNEZIA WG ==============="

# 1. Добавляем репозиторий и устанавливаем инструменты
export DEBIAN_FRONTEND=noninteractive
apt-get update >/dev/null 2>&1
apt-get install -y software-properties-common curl jq iptables-persistent >/dev/null 2>&1
add-apt-repository ppa:amnezia/ppa -y >/dev/null 2>&1
apt-get update >/dev/null 2>&1
apt-get install -y amneziawg-tools amneziawg-go qrencode >/dev/null 2>&1

echo "[+] Пакеты установлены"

# 2. Генерируем ключи
SERVER_PRIVKEY=$(awg genkey)
SERVER_PUBKEY=$(echo $SERVER_PRIVKEY | awg pubkey)
CLIENT_PRIVKEY=$(awg genkey)
CLIENT_PUBKEY=$(echo $CLIENT_PRIVKEY | awg pubkey)
CLIENT_PRESHARED=$(awg genpsk)

AWG_PORT=51820

# 3. Конфиг сервера
mkdir -p /etc/amnezia/amneziawg
cat > /etc/amnezia/amneziawg/awg0.conf <<EOF
[Interface]
PrivateKey = $SERVER_PRIVKEY
Address = 10.8.0.1/24
ListenPort = $AWG_PORT
Jc = 4
Jmin = 40
Jmax = 70
S1 = 29
S2 = 15
H1 = 2147483648
H2 = 1073741824
PostUp = iptables -A FORWARD -i awg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i awg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = $CLIENT_PUBKEY
PresharedKey = $CLIENT_PRESHARED
AllowedIPs = 10.8.0.2/32
EOF

echo "[+] Ключи и конфиг сервера сгенерированы"

# 4. Конфиг клиента
SERVER_IP=$(curl -s ifconfig.me)

cat > /root/родственник_vpn.conf <<EOF
[Interface]
PrivateKey = $CLIENT_PRIVKEY
Address = 10.8.0.2/32
DNS = 1.1.1.1, 8.8.8.8
Jc = 4
Jmin = 40
Jmax = 70
S1 = 29
S2 = 15
H1 = 2147483648
H2 = 1073741824

[Peer]
PublicKey = $SERVER_PUBKEY
PresharedKey = $CLIENT_PRESHARED
Endpoint = $SERVER_IP:$AWG_PORT
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
EOF

echo "[+] Файл родственник_vpn.conf создан"

# 5. Применяем правила безопасности (iptables) к VPN-интерфейсу 
echo "[+] Настраиваем фаервол (блокировка торрентов и спама) ..."

# Очистка старых (на всякий случай)
iptables -D FORWARD -i awg0 -p tcp --dport 25 -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -p tcp --dport 465 -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -p tcp --dport 587 -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -m string --algo bm --string "BitTorrent" -j DROP 2>/dev/null
iptables -D FORWARD -i awg0 -p udp -m multiport --dports 6881:6889 -j DROP 2>/dev/null

# Запрещаем почтовый Спам (порты 25, 465, 587)
iptables -I FORWARD 1 -i awg0 -p tcp --dport 25 -j DROP
iptables -I FORWARD 2 -i awg0 -p tcp --dport 465 -j DROP
iptables -I FORWARD 3 -i awg0 -p tcp --dport 587 -j DROP

# Блокировка стандартных Торрент-портов и P2P-сигнатур
iptables -I FORWARD 4 -i awg0 -p udp -m multiport --dports 6881:6889 -j DROP
iptables -I FORWARD 5 -i awg0 -p tcp -m multiport --dports 6881:6889 -j DROP
iptables -I FORWARD 6 -i awg0 -m string --algo bm --string "BitTorrent protocol" -j DROP || true

# Сохраняем правила iptables
iptables-save > /etc/iptables/rules.v4

# 6. Включаем форвардинг
sysctl -w net.ipv4.ip_forward=1 >/dev/null
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

# 7. Запускаем AmneziaWG
systemctl enable --now awg-quick@awg0 >/dev/null 2>&1

echo ""
echo "================================================="
echo "✅ AmneziaWG УСТАНОВЛЕН И ЗАЩИЩЕН ОТ ТОРРЕНТОВ!"
echo "================================================="
echo "Отсканируй этот QR-код камерой приложения AmneziaWG:"
echo ""
qrencode -t ANSIUTF8 < /root/родственник_vpn.conf
echo ""
echo "Конфигурационный файл также сохранен на сервере: /root/родственник_vpn.conf"
echo "================================================="
