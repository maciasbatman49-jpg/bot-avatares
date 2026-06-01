import os
from telegram.ext import Application

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

print("Bot iniciado - PRUEBA NUCLEAR")
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.run_polling()
