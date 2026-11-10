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
    print("Бот запущено і починає перевірку OLX...")
    
    # Покращені заголовки, щоб обійти захист від ботів
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    for target in TARGETS:
        print(f"Перевіряємо запит: {target['name']}")
        try:
            response = requests.get(target["url"], headers=headers)
            print(f"Статус відповіді OLX: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Помилка завантаження сторінки для {target['name']}. Код: {response.status_code}")
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
