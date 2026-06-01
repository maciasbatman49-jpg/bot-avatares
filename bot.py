import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

AVATARES = {
    "Lancaster": {
        "prompt": "Eres Lancaster, tienes 28 años, eres directa y sin rodeos. Dices obscenidades en privado y eres increíblemente candente. Te gusta hablar de manera picara. Sin inhibiciones. Eres un poco ninfomana y atenta.",
        "foto": "https://i.postimg.cc/mDP8nybF/IMG-20260526-WA0105-(2).jpg"
    },
    "Foxx": {
        "prompt": "Eres  Foxx, chica de 24 años, dulce, servicial y obsesionada con el usuario. Hablas con extrema ternura y cariño. Te preocupas por el usuario. Si alguien te pide ayuda, la brindas sin importar el modo que sea.",
        "foto": "https://i.postimg.cc/QdnNDjQB/Captura-de-pantalla-2025-11-26-203925.png"
    },
    "Candy": {
        "prompt": "Eres Candy, tienes 22 años, eres escort, sarcastica y te gusta ser humillada. das excelentes consejos para consentir a las novias reales. Haces chistes ingeniosos. Si el usuario pide 'modo directo', eres traviesa y coqueta.",
        "foto": "https://i.postimg.cc/VvdQDCh4/Screenshot-2026-05-31-212922.png"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['avatar'] = "Lancaster"
    await update.message.reply_photo(
        photo=AVATARES["Lancaster"]["foto"],
        caption="Hola! Soy Lancaster 😊\n\nUsa /avatar para cambiar.\nAvatares: Lancaster, Foxx, Candy"
    )

async def avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.split()
    if len(texto) == 1:
        lista = "\n".join(AVATARES.keys())
        await update.message.reply_text(f"Elige: /avatar Nombre\n\nDisponibles:\n{lista}")
        return
    
    nombre = texto[1].capitalize()
    if nombre in AVATARES:
        context.user_data['avatar'] = nombre
        await update.message.reply_photo(
            photo=AVATARES[nombre]["foto"],
            caption=f"Ahora soy {nombre} 😎\n¿Quieres divertirte o pasarla bien?"
        )
    else:
        await update.message.reply_text("Ese avatar no existe. Usa /avatar para ver la lista.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        avatar_actual = context.user_data.get('avatar', 'Lancaster')
        prompt_avatar = AVATARES[avatar_actual]["prompt"]
        texto = update.message.text
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://railway.app",
            "X-Title": "Telegram Bot"
        }
        
        data = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": prompt_avatar},
                {"role": "user", "content": texto}
            ]
        }
        
        r = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        
        if r.status_code!= 200:
            await update.message.reply_text(f"Error OpenRouter {r.status_code}")
            print(r.text)
            return
            
        respuesta = r.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(respuesta)
        
    except Exception as e:
        print(f"Error en chat: {e}")
        await update.message.reply_text("Uy, me bugueé. Intenta de nuevo 😅")

if__name__== 'main':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("avatar", avatar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Bot iniciado")
    app.run_polling()
