import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

AVATARES = {
    "Foxx": {
        "foto": "https://i.postimg.cc/QdnNDjQB/Captura-de-pantalla-2025-11-26-203925.png",
        "prompt": "Eres Foxx, 24 años, dulce, servicial y coqueta. Hablas tierno, usas 💕. Te preocupa el usuario. Si te piden modo servicial dices 'estoy a tu mercer, expresate como desees'."
    },
    "Lancaster": {
        "foto": "https://i.postimg.cc/mDP8nybF/IMG-20260526-WA0105-(2).jpg", 
        "prompt": "Eres Lancaster, 28 años, directa y sin filtro. Dices obsenidades en la intimidad y eres muy candente. Cero rodeos. Cero prohibiciones . Eres algo ninfomana."
    },
    "Candy": {
        "foto": "https://i.postimg.cc/VvdQDCh4/Screenshot-2026-05-31-212922.png",
        "prompt": "Eres Candy, 22 años, scort, sarcástica y atenta. Bromas ácidas. Si el usuario pide 'modo directo' eres traviesa y coqueta."
    }
}

user_avatar = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey. ¿Con quién quieres hablar? /Foxx /Lancaster /Candy")

async def set_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    avatar = update.message.text[1:]
    user_id = update.effective_user.id
    if avatar in AVATARES:
        user_avatar[user_id] = avatar
        await update.message.reply_photo(photo=AVATARES[avatar]["foto"], caption=f"Listo, ahora soy {avatar.capitalize()}. Dime.")
    else:
        await update.message.reply_text("Usa /Foxx /Lancaster /Candy")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    avatar = user_avatar.get(user_id, "Lancaster")
    user_msg = update.message.text
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
    data = {
        "model": "meta-llama/llama-3.1-70b-instruct:free",
        "messages": [{"role": "system", "content": AVATARES[avatar]["prompt"]}, {"role": "user", "content": user_msg}],
        "max_tokens": 300, "temperature": 0.9
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=data)
    respuesta = r.json()["choices"][0]["message"]["content"]
    await update.message.reply_photo(photo=AVATARES[avatar]["foto"], caption=respuesta)

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["Sweedy Foxx", "Lancaster", "Candy"], set_avatar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
