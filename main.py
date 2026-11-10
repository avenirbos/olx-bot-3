import telebot

TELEGRAM_BOT_TOKEN = "9146281861:AAE5etSEY8RSU06yOKIbeth4gATngr12s4g"
TELEGRAM_CHAT_ID = "7987062433"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

try:
    bot.send_message(TELEGRAM_CHAT_ID, "🧪 Тестове повідомлення з GitHub Actions: зв'язок є!")
    print("✅ Повідомлення успішно відправлено в Telegram!")
except Exception as e:
    print(f"❌ Помилка відправки: {e}")
