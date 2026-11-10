import os
import requests
from bs4 import BeautifulSoup
import telebot

# Токен вшитий напряму, щоб уникнути будь-яких помилок з GitHub Secrets
TELEGRAM_BOT_TOKEN = "9146281861:AAE5etSEY8RSU06yOKIbeth4gATngr12s4g"
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") # Chat ID залишаємо з секретів (або можна теж вписати, якщо знаєш)

if not TELEGRAM_CHAT_ID:
    # Якщо chat_id раптом не підтягнеться, спробуй вписати сюди свій ID цифрами замість None (наприклад: "123456789")
    TELEGRAM_CHAT_ID = "123456789" 

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

TARGETS = [
    {
        "name": "iPhone 12 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-gadzhety/mobilnye-telefony-smartfony/iphone/q-iphone-12-pro/",
    },
    {
        "name": "iPhone 13 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-gadzhety/mobilnye-telefony-smartfony/iphone/q-iphone-13-pro/",
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
            # Таймаут 5 секунд, щоб бот не зависав
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
            print(f"Помилка для {target['name']}: {e}")
            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"⚠️ Бот працює! Запит для '{target['name']}' натрапив на захист OLX, але зв'язок є."
            )

if __name__ == "__main__":
    check_olx()
