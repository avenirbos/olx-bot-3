import os
import requests
from bs4 import BeautifulSoup
import telebot

# Отримуємо токен і chat_id з налаштувань GitHub Secrets
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("ПОМИЛКА: Не задано TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID у GitHub Secrets!")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Список товарів для моніторингу на OLX
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
    print("Бот запущено і починає перевірку OLX...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for target in TARGETS:
        print(f"Перевіряємо запит: {target['name']}")
        try:
            response = requests.get(target["url"], headers=headers)
            print(f"Статус відповіді OLX: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Помилка завантаження сторінки для {target['name']}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            ads = soup.select("div[data-cy='l-card']")
            print(f"Знайдено карток оголошень: {len(ads)}")

            # Надсилаємо звіт у Telegram
            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"🟢 Бот успішно перевірив OLX для '{target['name']}'. Знайдено оголошень на сторінці: {len(ads)}"
            )
            print("Повідомлення успішно надіслано в Telegram!")

        except Exception as e:
            print(f"Помилка під час обробки {target['name']}: {e}")

if __name__ == "__main__":
    check_olx()
