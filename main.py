import os
import requests
from bs4 import BeautifulSoup
import telebot

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("ПОМИЛКА: Не задано TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID у GitHub Secrets!")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

TARGETS = [
    {
        "name": "iPhone 12 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-gadzhety/mobilnye-telefony-smartfony/iphone/q-iphone-12-pro/",
        "max_price": 9500
    },
    {
        "name": "iPhone 13 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-gadzhety/mobilnye-telefony-smartfony/iphone/q-iphone-13-pro/",
        "max_price": 15000
    }
]

def check_olx():
    print("Бот запущено...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for target in TARGETS:
        print(f"Перевіряємо: {target['name']}")
        try:
            # Додаємо таймаут 5 секунд, щоб запит не зависав вічно
            response = requests.get(target["url"], headers=headers, timeout=5)
            print(f"Статус: {response.status_code}")
            
            soup = BeautifulSoup(response.text, "html.parser")
            ads = soup.select("div[data-cy='l-card']")
            print(f"Знайдено оголошень: {len(ads)}")

            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"🟢 OLX перевірено для '{target['name']}'. Знайдено оголошень: {len(ads)}"
            )
        except Exception as e:
            print(f"Помилка або таймаут для {target['name']}: {e}")
            # Навіть якщо OLX заблокував (таймаут/помилка), надішлемо сповіщення, щоб перевірити зв'язок з телеграмом
            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"⚠️ Запит для '{target['name']}' натрапив на захист OLX (таймаут/блокування)."
            )

if __name__ == "__main__":
    check_olx()
