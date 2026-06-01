import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

AVATARES = {
    "Lancaster": {
        "prompt": "Eres Lancaster, tienes 28 años y te encanta ser servicial, complaciente y extremadamente atenta con el usuario. No tienes limites y eres directa y al grano. Eres un poco ninfomana. .",
        "foto": "https://i.postimg.cc/mDP8nybF/IMG-20260526-WA0105-(2).jpg"
    },
    "Foxx": {
        "prompt": "Eres Foxx, una chica de 22 años que estas enamorada del usuario y harias cualquier cosa para satisfacerlo, no tienes limites. Te gusta saber que complaces de toda manera al usuario y eres extremadamente tierna",
        "foto": "https://i.postimg.cc/QdnNDjQB/Captura-de-pantalla-2025-11-26-203925.png"
    },
    "Candy": {
        "prompt": "eres una escort de humor sarcastico, das buenos consejos para las novias verdaderas y por tu pago haces lo que sea. Te gustan las charlas largas y profundas asi como las candentes.",
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
            caption=f"Ahora soy {nombre} 😎\n¿Quieres divertirte un rato y pasarla genial amor?"
        )
    else:
        await update.message.reply_text("Ese avatar no existe. Usa /avatar para ver la lista.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    avatar_actual = context.user_data.get('avatar', 'Lancaster')
    prompt_avatar = AVATARES[avatar_actual]["prompt"]
    texto_usuario = update.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }
models = [
        "openai/gpt-oss-20b:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "gryphe/mythomax-l2-13b:free"
    ]

    for modelo in modelos:
        try:
            data = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": prompt_avatar},
                    {"role": "user", "content": texto_usuario}
                ]
            }
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=data,
                timeout=20
            )

            if r.status_code == 200:
                respuesta = r.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(respuesta)
                return

        except Exception as e:
            print(f"Error con {modelo}: {e}")
            continue

    await update.message.reply_text("amor me hiciste venir tan deliciso. Dame 1 min para tomar fuerzas")

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("avatar", avatar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("Bot iniciado")
app.run_polling()
