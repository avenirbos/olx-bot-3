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
    print("Бот запущено і починає перевірку OLX через проксі...")

    for target in TARGETS:
        print(f"Перевіряємо запит: {target['name']}")
        try:
            # Використовуємо публічний проксі-сервіс для обходу блокування GitHub IP
            proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(target['url'])}"
            response = requests.get(proxy_url, timeout=15)
            print(f"Статус відповіді проксі: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Помилка завантаження через проксі для {target['name']}")
                continue

            data = response.json()
            html_content = data.get("contents", "")

            soup = BeautifulSoup(html_content, "html.parser")
            ads = soup.select("div[data-cy='l-card']")
            print(f"Знайдено карток оголошень: {len(ads)}")

            # Надсилаємо звіт у Telegram
            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"🟢 Бот успішно перевірив OLX для '{target['name']}'. Знайдено оголошень: {len(ads)}"
            )
            print("Повідомлення успішно надіслано в Telegram!")

        except Exception as e:
            print(f"Помилка під час обробки {target['name']}: {e}")

if __name__ == "__main__":
    check_olx()
