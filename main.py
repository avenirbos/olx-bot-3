import requests
from bs4 import BeautifulSoup

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
    print("Бот запущено і починає перевірку OLX...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for target in TARGETS:
        print(f"\n--- Перевіряємо запит: {target['name']} ---")
        try:
            response = requests.get(target["url"], headers=headers, timeout=5)
            print(f"Статус відповіді OLX: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                ads = soup.select("div[data-cy='l-card']")
                print(f"✅ Успішно! Знайдено карток оголошень: {len(ads)}")
            else:
                print(f"⚠️ Сайт відповів зі статусом: {response.status_code}")

        except Exception as e:
            print(f"❌ Помилка під час запиту для {target['name']}: {e}")

if __name__ == "__main__":
    check_olx()
