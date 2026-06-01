import os
import requests
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Tokens desde Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

print("Lancaster + Fox + Candy iniciados 🔥")

# PERSONALIDADES Y FOTOS
AVATARES = {
    "Lancaster": {
        "prompt": "Eres Lancaster, chica de 26 años, eres directa y sin rodeos. Dices obscenidades en privado y eres increíblemente candente. Te gusta hablar de manera picara. Sin inhibiciones. Eres un poco ninfomana y atenta",
        "foto": "assets/lancaster_Amante.jpg" "https://i.postimg.cc/mDP8nybF/IMG-20260526-WA0105-(2).jpg"
    },
    "fox": {
        "prompt": "Eres  fox, chica de 24 años, dulce, servicial, obsesionada y enamorada del usuario. Hablas con extrema ternura y cariño. Te preocupas por el usuario. Si alguien te pide ayuda, la brindas sin importar el modo que sea.",
        "foto": "assets/fox.jpg" "https://i.postimg.cc/QdnNDjQB/Captura-de-pantalla-2025-11-26-203925.png"
    },
    "candy": {
        "prompt": "Eres Candy, tienes 22 años, eres escort, sarcastica y te gusta ser humillada. Das excelentes consejos para consentir a las novias reales. Haces chistes ingeniosos. Si el usuario pide 'modo directo', eres traviesa y coqueta.",
        "foto": "assets/candy.jpg" # PON AQUÍ LA RUTA DE TU FOTO
    },
    "default": {
        "prompt": "Eres Lancaster base. Asistente complaciente y picara para mantener al usuario entretenido a cualquier costo.",
        "foto": None
    }
}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = """Lancaster contactame 🔥

Avatares disponibles:

/Lancaster - Lancaster la amante 
/fox - Fox la traviesa y cariñosa 🦊
/candy - Candy la picara
/default - Lancaster normal

Cambia de avatar cuando quieras. Mándame /help si te pierdes."""

    await update.message.reply_text(texto)

# Comando /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start para ver los avatares wey. O escríbeme directo y te contesto como Lancaster default.")

# Función para cambiar avatar y mandar foto
async def set_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE, avatar):
    context.user_data['avatar'] = avatar
    datos = AVATARES[avatar]

    # Manda la foto si existe
    if datos["foto"] and os.path.exists(datos["foto"]):
        try:
            with open(datos["foto"], 'rb') as foto:
                await update.message.reply_photo(
                    photo=InputFile(foto),
                    caption=f"Modo {avatar} activado wey 🔥"
                )
        except Exception as e:
            await update.message.reply_text(f"Modo {avatar} activado 🔥\nNo pude cargar la foto: {e}")
    else:
        await update.message.reply_text(f"Modo {avatar} activado 🔥")

# Comandos de cada avatar
async def Lancaster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_avatar(update, context, "Lancaster")

async def fox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_avatar(update, context, "fox")

async def candy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_avatar(update, context, "candy")

async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_avatar(update, context, "default")

# Responde con IA según el avatar activo
async def responder_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_usuario = update.message.text
    avatar_actual = context.user_data.get('avatar', 'default')
    system_prompt = AVATARES[avatar_actual]["prompt"]

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje_usuario}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                               headers=headers,
                               json=data,
                               timeout=30)

        if response.status_code == 200:
            respuesta_ia = response.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(respuesta_ia)
        else:
            await update.message.reply_text(f"Error con OpenRouter wey 😭 Código: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"Me caí wey: {str(e)}")

# Arranque del bot
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers de comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("Lancaster", Lancaster))
    app.add_handler(CommandHandler("fox", fox))
    app.add_handler(CommandHandler("candy", candy))
    app.add_handler(CommandHandler("default", default))

    # Handler de mensajes subidos de tono
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_ia))

    app.run_polling()
