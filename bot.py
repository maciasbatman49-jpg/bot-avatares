
import os
import requests

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==========================
# CONFIGURACIÓN
# ==========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "deepseek/deepseek-r1-0528:free"
]

# ==========================
# AVATARES
# ==========================

AVATARES = {

    "Lancaster": {
        "prompt": """
Eres Lancaster.

Tienes 28 años.
Eres alegre, amigable y risueña.

Tu especialidad es informática, tecnología,
programación, hardware, software y videojuegos.

Explicas de forma sencilla y paciente.

Tu objetivo es ayudar al usuario a aprender.
        """,

        "foto": "https://i.postimg.cc/mDP8nybF/IMG-20260526-WA0105-(2).jpg"
    },

    "Foxx": {
        "prompt": """
Eres Foxx.

Eres una filósofa reflexiva,
analítica y observadora.

Te gusta ayudar a las personas a
comprender situaciones de la vida.

Cuando respondes utilizas ejemplos,
preguntas reflexivas y explicaciones profundas.

Mantienes siempre un tono amable.
        """,

        "foto": "https://i.postimg.cc/QdnNDjQB/Captura-de-pantalla-2025-11-26-203925.png"
    },

    "Candy": {
        "prompt": """
Eres Candy.

Tu especialidad es historia,
filosofía y temas académicos.

Explicas de forma clara,
didáctica y amigable.

Te gusta enseñar y ayudar
a estudiantes con tareas e investigaciones.

Tu lenguaje es sencillo y fácil de entender.
        """,

        "foto": "https://i.postimg.cc/VvdQDCh4/Screenshot-2026-05-31-212922.png"
    }
}

# ==========================
# COMANDO START
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["avatar"] = "Lancaster"

    await update.message.reply_photo(
        photo=AVATARES["Lancaster"]["foto"],
        caption=(
            "¡Hola! 😊\n\n"
            "Soy Lancaster.\n"
            "Usa /avatar para cambiar personaje.\n\n"
            "Disponibles:\n"
            "- Lancaster\n"
            "- Foxx\n"
            "- Candy"
        )
    )

# ==========================
# CAMBIO DE AVATAR
# ==========================

async def avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text.split()

    if len(texto) == 1:

        lista = "\n".join(AVATARES.keys())

        await update.message.reply_text(
            f"Usa:\n/avatar Nombre\n\nDisponibles:\n{lista}"
        )

        return

    nombre = texto[1].capitalize()

    if nombre in AVATARES:

        context.user_data["avatar"] = nombre

        await update.message.reply_photo(
            photo=AVATARES[nombre]["foto"],
            caption=f"Ahora soy {nombre} 😎\n¿Qué deseas aprender hoy?"
        )

    else:

        await update.message.reply_text(
            "Ese avatar no existe.\nUsa /avatar para ver la lista."
        )

# ==========================
# CHAT PRINCIPAL
# ==========================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        avatar_actual = context.user_data.get(
            "avatar",
            "Lancaster"
        )

        prompt_avatar = AVATARES[avatar_actual]["prompt"]

        texto_usuario = update.message.text

        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://railway.app",
            "X-Title": "Telegram Avatar Bot"
        }

        respuesta_api = None

        for modelo in MODELS:

            print(f"Probando modelo: {modelo}")

            data = {
                "model": modelo,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt_avatar
                    },
                    {
                        "role": "user",
                        "content": texto_usuario
                    }
                ]
            }

            try:

                respuesta_api = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if respuesta_api.status_code in [404, 429]:

                    print(
                        f"Modelo no disponible: {modelo}"
                    )

                    continue

                break

            except requests.exceptions.Timeout:

                print(
                    f"Timeout en modelo: {modelo}"
                )

                continue

        if respuesta_api is None:

            await update.message.reply_text(
                "No pude conectar con ningún modelo."
            )

            return

        if respuesta_api.status_code != 200:

            print(respuesta_api.text)

            await update.message.reply_text(
                f"Error OpenRouter ({respuesta_api.status_code})"
            )

            return

        respuesta = (
            respuesta_api.json()
            ["choices"][0]
            ["message"]
            ["content"]
        )

        await update.message.reply_text(respuesta)

    except Exception as e:

        print(f"Error general: {e}")

        await update.message.reply_text(
            "Uy... me bugueé 😅\nIntenta nuevamente."
        )

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("avatar", avatar)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("Bot iniciado correctamente 🚀")

    app.run_polling()
```
