import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Учетные данные Hostoff.net (из SETUP_SUMMARY.md)
HOSTOFF_URL = "https://panel.hostoff.net/billmgr"
# Эти данные лучше добавить в .env, но пока возьмем из того что знаем
HOSTOFF_USER = "gibertlega@gmail.com"
HOSTOFF_PASS = "GibertLega221633"

def get_hostoff_balance():
    try:
        # 1. Авторизация и получение сессии
        auth_url = f"{HOSTOFF_URL}?out=json&func=auth&username={HOSTOFF_USER}&password={HOSTOFF_PASS}"
        response = requests.get(auth_url, verify=True)
        try:
            data = response.json()
        except Exception:
            return f"Ошибка парсинга JSON: {response.text[:500]}"
        
        if 'doc' in data and 'auth' in data['doc'] and 'session' in data['doc']['auth']:
            session = data['doc']['auth']['session']['$']
        else:
            return "Ошибка авторизации: не удалось получить сессию."

        # 2. Запрос информации об аккаунте (там обычно лежит баланс)
        # В BillManager 6 баланс часто лежит в ответе функции 'account'
        account_url = f"{HOSTOFF_URL}?out=json&func=account&auth={session}"
        account_response = requests.get(account_url, verify=True)
        account_data = account_response.json()
        
        # Парсим баланс. В BillManager структура может быть вложенной.
        # Обычно это doc -> account -> balance
        balance = "Не найдено"
        if 'doc' in account_data and 'account' in account_data['doc']:
            balance = account_data['doc']['account'].get('balance', {}).get('$', '0.00')
            currency = account_data['doc']['account'].get('currency_iso', {}).get('$', 'RUB')
            return f"{balance} {currency}"
        
        return "Баланс не найден в ответе API."

    except Exception as e:
        return f"Ошибка при запросе баланса: {str(e)}"

if __name__ == "__main__":
    balance = get_hostoff_balance()
    print(f"Текущий баланс на Hostoff.net: {balance}")
