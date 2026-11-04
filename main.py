
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import (Application,CommandHandler,MessageHandler,ContextTypes,filters)

# 1. Charger les variables d'environnement
load_dotenv()

# 2. Récupérer le token Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")


# 3. Fonction qui répond à la commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salut ! 👋 Bienvenue sur mon bot de téléchargement vidéo."
    )


# 4. Fonction principale
def main():
    # Créer notre application Telegram
    app = Application.builder().token(TOKEN).build()

    # Enregistrer la commande /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))
    # Démarrer le bot
    print("Le bot est démarré...")
    app.run_polling()



async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Récupérer le message envoyé par l'utilisateur
    url = update.message.text

    # Vérifier si le message contient un lien
    if url.startswith("http://") or url.startswith("https://"):

        await update.message.reply_text(
            f"J'ai reçu ton lien : {url}"
        )

    else:
        await update.message.reply_text(
            "Envoie-moi un lien vidéo valide."
        )

# 5. Exécuter le programme
if __name__ == "__main__":
    main()
