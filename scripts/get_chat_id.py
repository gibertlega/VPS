import paramiko
import json

HOST = "89.125.79.214"
USER = "root"
PASS = "GibertLega221633"
TOKEN = "8763168285:AAHb-2-a5HziTC-hCwng3wvZBQumOsVsLZc"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Подключаюсь к серверу...")
client.connect(HOST, username=USER, password=PASS, timeout=10)

cmd = f"curl -s https://api.telegram.org/bot{TOKEN}/getUpdates"
print("Отправляю запрос к Telegram API с сервера...")
_, stdout, stderr = client.exec_command(cmd)
response = stdout.read().decode().strip()

print(f"Ответ API: {response}")

try:
    data = json.loads(response)
    if not data.get("ok"):
        print("Ошибка API:", data)
    else:
        results = data.get("result", [])
        if not results:
            print("Нет новых сообщений! Напиши что-нибудь боту и попробуй снова.")
        else:
            last_message = results[-1]
            chat_id = last_message["message"]["chat"]["id"]
            username = last_message["message"]["chat"].get("username", "Неизвестно")
            text = last_message["message"].get("text", "")
            
            print(f"\n--- НАЙДЕН CHAT ID ---")
            print(f"Пользователь: @{username}")
            print(f"Текст сообщения: {text}")
            print(f"Твой CHAT ID: {chat_id}")
            print(f"------------------------\n")
            
            # Сохраняю в файл для .env
            with open("chat_id.txt", "w") as f:
                f.write(str(chat_id))
except Exception as e:
    print(f"Ошибка парсинга ответа: {e}")

client.close()
