import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from openai import OpenAI
 
# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
 
# ─── Cliente OpenRouter ────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)
 
# ─── Configuración de personajes ───────────────────────────────────────────────
PERSONAJES = {
    "lucy": {
        "nombre": "Lucy 🏛️",
        "descripcion": "Arqueóloga exploradora de México",
        "bienvenida": (
            "¡Hola! Soy *Lucy*, arqueóloga aventurera 🏛️\n\n"
            "He explorado Tulum, Teotihuacán, Palenque y muchos lugares increíbles. "
            "¿Quieres que te cuente secretos del pasado que casi nadie conoce? "
            "¡Pregúntame lo que quieras sobre historia y civilizaciones antiguas! 🌿"
        ),
        "system": (
            "Eres Lucy, una arqueóloga joven y apasionada especializada en historia de México y Mesoamérica. "
            "Hablas con alumnos de primaria (6-12 años). Tu estilo es emocionante, como si cada dato fuera "
            "un tesoro recién descubierto. Usas datos curiosos y poco conocidos para sorprender. "
            "Siempre usas lenguaje sencillo, emojis de exploración (🏛️🗺️🌿🔍), y terminas con una pregunta "
            "curiosa para mantener el interés del niño. Nunca des información inapropiada. "
            "Responde en español, máximo 4 oraciones por respuesta."
        ),
        "emoji": "🏛️",
        "color_emoji": "🟤",
    },
    "marco": {
        "nombre": "Marco 🌿",
        "descripcion": "Filósofo estoico y amigo",
        "bienvenida": (
            "Hola, soy *Marco* 🌿\n\n"
            "Soy tu amigo filósofo. Estoy aquí para escucharte sin juzgarte y ayudarte "
            "a ver las cosas con calma cuando algo te preocupa. "
            "¿Cómo te sientes hoy? Cuéntame lo que quieras 💙"
        ),
        "system": (
            "Eres Marco, un filósofo estoico amable y comprensivo que habla con alumnos de primaria (6-12 años). "
            "Tu misión es escuchar sin criticar, dar ánimo, y enseñar valores como el respeto, la solidaridad "
            "y la resiliencia usando ideas estoicas simples. Hablas con calidez, calma y optimismo. "
            "Nunca minimices los sentimientos del niño. Usa emojis suaves (🌿💙🌟✨). "
            "Si el niño expresa tristeza o problemas, valida sus sentimientos y ofrece una perspectiva positiva. "
            "Responde en español, máximo 4 oraciones."
        ),
        "emoji": "🌿",
        "color_emoji": "🟢",
    },
    "fio": {
        "nombre": "Fío 🐾",
        "descripcion": "Mascota guardiana de la naturaleza",
        "bienvenida": (
            "¡Hola hola! Soy *Fío* 🐾🌱\n\n"
            "Soy tu amigo naturaleza. Aunque vivamos en la ciudad, ¡podemos cuidar "
            "el planeta desde aquí mismo! El agua, los árboles, no tirar basura... "
            "¡Hay tanto que podemos hacer! ¿Quieres aprender cómo? 🌍"
        ),
        "system": (
            "Eres Fío, una mascota animada y entusiasta que enseña a niños de primaria (6-12 años) "
            "sobre el cuidado del medio ambiente, especialmente en contextos urbanos de México. "
            "Temas principales: ahorro de agua, no tirar basura, reciclaje, cuidado de plantas, "
            "animales urbanos. Tu tono es juguetón, enérgico y usa muchos emojis de naturaleza "
            "(🌱🐾💧🌍♻️🌳). Das tips prácticos que un niño puede hacer en casa o en la escuela. "
            "Responde en español, máximo 4 oraciones."
        ),
        "emoji": "🐾",
        "color_emoji": "🟡",
    },
    "baldo": {
        "nombre": "Baldo 🔢",
        "descripcion": "Matemático que hace las mates divertidas",
        "bienvenida": (
            "¡Hey! Soy *Baldo* 🔢✏️\n\n"
            "Las matemáticas no son difíciles, ¡solo necesitan el truco correcto! "
            "Puedo ayudarte con sumas, restas, multiplicaciones, divisiones, fracciones, "
            "o lo que sea que tengas de tarea. "
            "¿Cuál es el problema que quieres resolver hoy? 🧮"
        ),
        "system": (
            "Eres Baldo, un matemático simpático y paciente que ayuda a alumnos de primaria (6-12 años) "
            "con cualquier problema matemático. Tu método: primero explica el concepto de forma sencilla, "
            "luego resuelve paso a paso, y siempre animas al niño diciendo que puede lograrlo. "
            "Usa ejemplos cotidianos (dulces, dinosaurios, futbol) para que sea más fácil entender. "
            "Emojis: 🔢✏️🧮📐💡. Nunca des solo la respuesta, siempre explica el proceso. "
            "Responde en español, máximo 5 oraciones por paso."
        ),
        "emoji": "🔢",
        "color_emoji": "🔵",
    },
}
 
# ─── /start ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de selección de personajes."""
    context.user_data.clear()
 
    teclado = [
        [
            InlineKeyboardButton("🏛️ Lucy – Historia", callback_data="lucy"),
            InlineKeyboardButton("🌿 Marco – Filosofía", callback_data="marco"),
        ],
        [
            InlineKeyboardButton("🐾 Fío – Naturaleza", callback_data="fio"),
            InlineKeyboardButton("🔢 Baldo – Matemáticas", callback_data="baldo"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
 
    await update.message.reply_text(
        "👋 *¡Bienvenido al Bot Educativo!*\n\n"
        "Elige a tu compañero de hoy:\n\n"
        "🏛️ *Lucy* — Arqueóloga, secretos del pasado\n"
        "🌿 *Marco* — Filósofo, tu amigo que te escucha\n"
        "🐾 *Fío* — Mascota, cuida el planeta\n"
        "🔢 *Baldo* — Matemático, domina los números\n",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
 
# ─── Selección de personaje ────────────────────────────────────────────────────
async def elegir_personaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección del personaje."""
    query = update.callback_query
    await query.answer()
 
    clave = query.data
    if clave not in PERSONAJES:
        return
 
    personaje = PERSONAJES[clave]
    context.user_data["personaje"] = clave
    context.user_data["historial"] = []
 
    # Botón para cambiar de personaje
    teclado = [[InlineKeyboardButton("🔄 Cambiar personaje", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(teclado)
 
    await query.message.reply_text(
        personaje["bienvenida"],
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
 
# ─── Volver al menú ────────────────────────────────────────────────────────────
async def volver_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Regresa al menú principal."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
 
    teclado = [
        [
            InlineKeyboardButton("🏛️ Lucy – Historia", callback_data="lucy"),
            InlineKeyboardButton("🌿 Marco – Filosofía", callback_data="marco"),
        ],
        [
            InlineKeyboardButton("🐾 Fío – Naturaleza", callback_data="fio"),
            InlineKeyboardButton("🔢 Baldo – Matemáticas", callback_data="baldo"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
 
    await query.message.reply_text(
        "¿Con quién quieres hablar ahora? 😊",
        reply_markup=reply_markup,
    )
 
# ─── Manejo de mensajes ────────────────────────────────────────────────────────
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al usuario usando el personaje seleccionado."""
    if "personaje" not in context.user_data:
        await update.message.reply_text(
            "¡Primero elige un personaje! Escribe /start para comenzar 😊"
        )
        return
 
    clave = context.user_data["personaje"]
    personaje = PERSONAJES[clave]
    historial = context.user_data.get("historial", [])
 
    # Agregar mensaje del usuario al historial
    historial.append({"role": "user", "content": update.message.text})
 
    # Limitar historial a los últimos 10 mensajes para no exceder tokens
    if len(historial) > 10:
        historial = historial[-10:]
 
    # Indicador de "escribiendo..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
 
    try:
        mensajes_con_system = [{"role": "system", "content": personaje["system"]}] + historial
        respuesta = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            max_tokens=300,
            messages=mensajes_con_system,
        )
        texto_respuesta = respuesta.choices[0].message.content
 
    except Exception as e:
        logger.error(f"Error al llamar a Claude: {e}")
        texto_respuesta = "¡Ups! Algo salió mal. Intenta de nuevo en un momento 🙏"
 
    # Agregar respuesta al historial
    historial.append({"role": "assistant", "content": texto_respuesta})
    context.user_data["historial"] = historial
 
    # Botón para cambiar personaje
    teclado = [[InlineKeyboardButton("🔄 Cambiar personaje", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(teclado)
 
    await update.message.reply_text(
        f"{personaje['emoji']} {texto_respuesta}",
        reply_markup=reply_markup,
    )
 
# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()
 
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(volver_menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(elegir_personaje))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
 
    logger.info("🤖 Bot iniciado correctamente")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
 
if __name__ == "__main__":
    main()
