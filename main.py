import requests
from bs4 import BeautifulSoup
import telebot

TELEGRAM_BOT_TOKEN = "9146281861:AAE5etSEY8RSU06yOKIbeth4gATngr12s4g"
TELEGRAM_CHAT_ID = "7987062433"

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
            response = requests.get(target["url"], headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            ads = soup.select("div[data-cy='l-card']")
            
            # Відправляємо повідомлення в Telegram
            bot.send_message(
                TELEGRAM_CHAT_ID, 
                f"🟢 OLX перевірено для '{target['name']}'. Знайдено оголошень: {len(ads)}"
            )
            print(f"✅ Успішно надіслано в Telegram для {target['name']}")
        except Exception as e:
            print(f"Помилка для {target['name']}: {e}")

if __name__ == "__main__":
    check_olx()
