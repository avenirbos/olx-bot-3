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
    print("Бот запущено і починає перевірку OLX (мобільний профіль)...")
    
    # Використовуємо мобільний User-Agent, який менше блокується
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    for target in TARGETS:
        print(f"Перевіряємо запит: {target['name']}")
        try:
            response = requests.get(target["url"], headers=headers, timeout=10)
            print(f"Статус відповіді OLX: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Помилка завантаження: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            ads = soup.select("div[data-cy='l-card']")
            print(f"Знайдено карток оголошень: {len(ads)}")

            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"🟢 Бот успішно перевірив OLX для '{target['name']}'. Знайдено оголошень: {len(ads)}"
            )
            print("Повідомлення успішно надіслано в Telegram!")

        except Exception as e:
            print(f"Помилка під час обробки {target['name']}: {e}")

if __name__ == "__main__":
    check_olx()
