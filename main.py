import telebot

TELEGRAM_BOT_TOKEN = "9146281861:AAE5etSEY8RSU06yOKIbeth4gATngr12s4g"
TELEGRAM_CHAT_ID = "7987062433"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
bot.send_message(TELEGRAM_CHAT_ID, "🔥 УРА! Зв'язок з GitHub Actions встановлено!")
print("Повідомлення надіслано!")
