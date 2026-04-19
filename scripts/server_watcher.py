import time
import datetime

def get_free_ram():
    # Эта функция читает системный файл Linux с информацией о памяти
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
        # Извлекаем строчку MemFree (свободно), конвертируем из Килобайт в Мегабайты
        free_ram = int(lines[1].split()[1]) / 1024 
        return round(free_ram)

log_file = "/root/watcher_log.txt"

# Записываем первое приветствие
with open(log_file, 'a', encoding='utf-8') as f:
    f.write(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 🚀 Скрипт успешно запущен Тотал Коммандером!\n")

print("Скрипт запущен! Логи пишутся в /root/watcher_log.txt")

# Бесконечный цикл (работает 24/7)
while True:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    ram = get_free_ram()
    text = f"[{now}] Я жив! У сервера свободно ОЗУ: {ram} МБ\n"
    
    # Открываем лог-файл, дописываем строчку и закрываем
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(text)
    
    # Засыпаем ровно на 60 секунд до следующей проверки
    time.sleep(60)
