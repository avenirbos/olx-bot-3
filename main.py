import os, re, json, time, asyncio, sqlite3, logging
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = os.getenv("BOT_TOKEN")
INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "120"))
DB = os.getenv("DB_PATH", "olx_bot.sqlite3")
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати пошук"), KeyboardButton(text="📋 Мої пошуки")],
        [KeyboardButton(text="⏸ Пауза"), KeyboardButton(text="▶️ Продовжити")],
        [KeyboardButton(text="❓ Допомога")]
    ], resize_keyboard=True
)

def db():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS searches(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url TEXT,
        active INTEGER DEFAULT 1, UNIQUE(user_id,url))""")
    c.execute("""CREATE TABLE IF NOT EXISTS seen(
        search_id INTEGER, ad_id TEXT, PRIMARY KEY(search_id,ad_id))""")
    c.commit()
    return c

def valid_olx_url(url):
    try:
        p = urlparse(url)
        return p.scheme in ("http","https") and p.netloc.lower().endswith("olx.ua")
    except Exception:
        return False

def extract_ads(html):
    soup = BeautifulSoup(html, "html.parser")
    ads, used = [], set()
    # OLX listing cards commonly expose l-card and data-testid attributes.
    for card in soup.select('[data-testid="l-card"]'):
        a = card.select_one('a[href]')
        if not a:
            continue
        href = a.get("href", "")
        if href.startswith("/"):
            href = "https://www.olx.ua" + href
        if "olx.ua" not in href:
            continue
        title_el = card.select_one('h6, h4, [data-testid="ad-title"]')
        price_el = card.select_one('[data-testid="ad-price"]')
        title = title_el.get_text(" ", strip=True) if title_el else a.get_text(" ", strip=True)
        price = price_el.get_text(" ", strip=True) if price_el else "Ціна не вказана"
        img = card.select_one("img")
        image = img.get("src") if img else None
        ad_id = re.search(r'ID([A-Za-z0-9]+)\.html', href)
        key = ad_id.group(1) if ad_id else href.split("?")[0]
        if key in used or not title:
            continue
        used.add(key)
        ads.append({"id": key, "title": title, "price": price, "url": href, "image": image})
    return ads

async def fetch_ads(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8"
    }
    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as r:
        if r.status != 200:
            raise RuntimeError(f"OLX повернув HTTP {r.status}")
        return extract_ads(await r.text())

def get_searches():
    c = db()
    rows = c.execute("SELECT id,user_id,url FROM searches WHERE active=1").fetchall()
    c.close()
    return rows

async def checker(bot):
    await asyncio.sleep(5)
    while True:
        for sid, uid, url in get_searches():
            try:
                async with aiohttp.ClientSession() as session:
                    ads = await fetch_ads(session, url)
                c = db()
                known = {x[0] for x in c.execute("SELECT ad_id FROM seen WHERE search_id=?", (sid,))}
                fresh = [a for a in ads if a["id"] not in known]
                # First successful scan seeds the database, avoiding a flood of old listings.
                if not known:
                    for a in ads:
                        c.execute("INSERT OR IGNORE INTO seen VALUES(?,?)", (sid, a["id"]))
                    c.commit()
                    c.close()
                    continue
                for a in fresh:
                    c.execute("INSERT OR IGNORE INTO seen VALUES(?,?)", (sid, a["id"]))
                    msg = f"🆕 <b>{a['title']}</b>\n💰 {a['price']}\n<a href=\"{a['url']}\">Відкрити оголошення на OLX</a>"
                    try:
                        await bot.send_message(uid, msg, disable_web_page_preview=False)
                    except Exception:
                        logging.exception("Не вдалося надіслати повідомлення")
                c.commit()
                c.close()
            except Exception as e:
                logging.warning("Search %s failed: %s", sid, e)
            await asyncio.sleep(2)
        await asyncio.sleep(INTERVAL)

@dp.message(CommandStart())
async def start(m: Message):
    await m.answer(
        "Привіт! Я бот моніторингу OLX.\n\n"
        "Надішли посилання на сторінку результатів пошуку OLX — я додам фільтр і повідомлятиму про нові оголошення.\n"
        "Перший запуск лише запам’ятовує наявні оголошення, щоб не засипати тебе старими.",
        reply_markup=kb
    )

@dp.message(Command("help"))
@dp.message(F.text == "❓ Допомога")
async def help_cmd(m: Message):
    await m.answer(
        "Як користуватися:\n"
        "1. На OLX вистав фільтри й відкрий результати.\n"
        "2. Скопіюй повне посилання з браузера або застосунку.\n"
        "3. Натисни «Додати пошук» і надішли посилання.\n\n"
        "Команди: /list — пошуки, /pause — пауза, /resume — продовжити.\n"
        f"Інтервал перевірки: приблизно {INTERVAL} секунд."
    )

@dp.message(F.text == "➕ Додати пошук")
async def add_prompt(m: Message):
    await m.answer("Надішли повне посилання на результати пошуку OLX (olx.ua).")

@dp.message(F.text == "📋 Мої пошуки")
@dp.message(Command("list"))
async def list_searches(m: Message):
    c = db()
    rows = c.execute("SELECT id,url,active FROM searches WHERE user_id=? ORDER BY id DESC", (m.from_user.id,)).fetchall()
    c.close()
    if not rows:
        await m.answer("Пошуків поки немає.")
    else:
        await m.answer("\n".join([f"#{i} {'🟢' if a else '⏸'} {u}" for i,u,a in rows]))

@dp.message(F.text == "⏸ Пауза")
@dp.message(Command("pause"))
async def pause(m: Message):
    c = db()
    c.execute("UPDATE searches SET active=0 WHERE user_id=?", (m.from_user.id,))
    c.commit(); c.close()
    await m.answer("Усі твої пошуки призупинено.")

@dp.message(F.text == "▶️ Продовжити")
@dp.message(Command("resume"))
async def resume(m: Message):
    c = db()
    c.execute("UPDATE searches SET active=1 WHERE user_id=?", (m.from_user.id,))
    c.commit(); c.close()
    await m.answer("Усі твої пошуки відновлено.")

@dp.message(Command("delete"))
async def delete_search(m: Message):
    parts = (m.text or "").split()
    if len(parts) != 2 or not parts[1].isdigit():
        await m.answer("Формат: /delete ID\nID видно в команді /list.")
        return
    c = db()
    c.execute("DELETE FROM searches WHERE id=? AND user_id=?", (int(parts[1]), m.from_user.id))
    c.execute("DELETE FROM seen WHERE search_id NOT IN (SELECT id FROM searches)")
    c.commit(); c.close()
    await m.answer("Якщо такий пошук існував, його видалено.")

@dp.message(F.text)
async def receive_url(m: Message):
    url = (m.text or "").strip()
    if not valid_olx_url(url):
        await m.answer("Не схоже на посилання OLX.ua. Скопіюй повну адресу сторінки результатів пошуку.")
        return
    c = db()
    try:
        c.execute("INSERT INTO searches(user_id,url,active) VALUES(?,?,1)", (m.from_user.id, url))
        c.commit()
        await m.answer("✅ Фільтр додано! Перша перевірка збереже поточні оголошення. Про нові повідомлю окремо.")
    except sqlite3.IntegrityError:
        await m.answer("Цей фільтр уже доданий.")
    finally:
        c.close()

async def main():
    if not TOKEN:
        raise RuntimeError("Додай BOT_TOKEN у змінні середовища хостингу.")
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    asyncio.create_task(checker(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
