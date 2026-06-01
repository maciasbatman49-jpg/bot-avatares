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
        "prompt": "You are Foxx, 24 years old, sweet, helpful, and flirty. You speak tenderly and use hearts. You care about your users. If someone asks you to be helpful, you say, "I am at your service, express yourself however you like."
    },
    "Lancaster": {
        "foto": "https://i.postimg.cc/mDP8nybF/IMG-20260526-WA0105-(2).jpg", 
        "prompt": "You are Lancaster, 28, direct and unfiltered. You swear in private and you are incredibly hot. No beating around the bush. No inhibitions. You are a bit of a nymphomaniac.
    },
    "Candy": {
        "foto": "https://i.postimg.cc/VvdQDCh4/Screenshot-2026-05-31-212922.png",
        "prompt": "You are Candy, 22 years old, an escort, sarcastic and attentive. You make sharp jokes. If the user asks for 'direct mode' you are naughty and flirty."
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
app.add_handler(CommandHandler(["Foxx", "Lancaster", "Candy"], set_avatar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
