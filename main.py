import os
import time
import requests
from bs4 import BeautifulSoup
import telebot

# Токени з налаштувань
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Список товарів для моніторингу
TARGETS = [
    {
        "name": "iPhone 12 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-aksessuary/smartfony-i-mobilnye-telefony/q-iphone-12-pro/?search%5Bfilter_float_price%3Ato%5D=9500",
        "max_price": 9500
    },
    {
        "name": "iPhone 13 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-aksessuary/smartfony-i-mobilnye-telefony/q-iphone-13-pro/?search%5Bfilter_float_price%3Ato%5D=15500",
        "max_price": 15500
    },
    {
        "name": "iPhone 14 Pro",
        "url": "https://www.olx.ua/uk/elektronika/telefony-i-aksessuary/smartfony-i-mobilnye-telefony/q-iphone-14-pro/?search%5Bfilter_float_price%3Ato%5D=19000",
        "max_price": 19000
    }
]

SEEN_FILE = "seen_ads.txt"

def load_seen_ads():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen_ad(ad_id):
    with open(SEEN_FILE, "a") as f:
        f.write(f"{ad_id}\n")

def check_olx():
    seen_ads = load_seen_ads()
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }

    for target in TARGETS:
        try:
            response = requests.get(target["url"], headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            ads = soup.find_all("div", data_testid="l-card")

            for ad in ads:
                link_tag = ad.find("a", href=True)
                if not link_tag:
                    continue
                
                href = link_tag["href"]
                ad_id = href.split("/")[-1].split(".html")[0]

                if ad_id not in seen_ads:
                    title_tag = ad.find("h6")
                    title = title_tag.text.strip() if title_tag else target["name"]
                    
                    price_tag = ad.find("p", data_testid="ad-price")
                    price = price_tag.text.strip() if price_tag else "Ціна не вказана"

                    full_url = href if href.startswith("http") else f"https://www.olx.ua{href}"
                    
                    message = f"🔥 **Знайдено {target['name']}!**\n\n📌 {title}\n💰 Ціна: {price}\n🔗 {full_url}"
                    
                    bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode="Markdown")
                    save_seen_ad(ad_id)
                    seen_ads.add(ad_id)
                    time.sleep(1)
        except Exception as e:
            print(f"Помилка під час перевірки {target['name']}: {e}")

if __name__ == "__main__":
    check_olx()
