import os
from dotenv import load_dotenv
from telegram import update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()


TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salut ! 👋 Bienvenue sur mon bot de téléchargement vidéo. Tu es chez toi "
    )