
import os
import asyncio
import logging

from pathlib import Path
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# 1. Charger les variables d'environnement
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

# 2. Dossier où les vidéos seront téléchargées
DOWNLOAD_DIR = Path("downloads")

# Limite indicative de Telegram Bot API
MAX_SIZE = 50 * 1024 * 1024
# autorise au maximum deux téléchargements simultanés
DOWNLOAD_SEMAPHORE = asyncio.Semaphore(2)

# 3. Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Salut ! \n\n"
        "Envoie-moi un lien vidéo et je vais essayer de la télécharger."
    )


# 4. Fonction de téléchargement avec yt-dlp
def download_video(url: str):

    DOWNLOAD_DIR.mkdir(exist_ok=True)

    options = {
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(options) as ydl:

        info = ydl.extract_info(url, download=True)

        video_id = info.get("id")
        title = info.get("title", "Vidéo")

    # Retrouver le fichier téléchargé
    files = list(DOWNLOAD_DIR.glob(f"{video_id}.*"))

    if not files:
        raise FileNotFoundError("Vidéo introuvable après téléchargement.")

    video_path = max(files, key=lambda file: file.stat().st_size)

    return video_path, title


# 5. Recevoir et télécharger le lien
async def receive_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    url = update.message.text.strip()

    # Vérifier le format du lien
    if not url.startswith(("https://", "http://")):

        await update.message.reply_text(
            "Envoie-moi un lien HTTP ou HTTPS valide."
        )
        return

    # Informer l'utilisateur
    status = await update.message.reply_text(
        " Téléchargement en cours..."
    )

    video_path = None

    try:

        # Exécuter yt-dlp sans bloquer le bot
        video_path, title = await asyncio.to_thread(
            download_video,
            url
        )

        # Vérifier la taille du fichier
        file_size = video_path.stat().st_size

        if file_size > MAX_SIZE:

            await status.edit_text(
                "Désolé, cette vidéo dépasse la limite "
                "de 50 Mo de notre bot."
            )
            return

        # Envoyer la vidéo sur Telegram
        with video_path.open("rb") as video:

            if video_path.suffix.lower() == ".mp4":

                await update.message.reply_video(
                    video=video,
                    caption=f" {title}"
                )

            else:

                await update.message.reply_document(
                    document=video,
                    caption=f" {title}"
                )

        await status.delete()

    except Exception:

        logging.exception("Erreur pendant le téléchargement")

        await status.edit_text(
            " Impossible de télécharger cette vidéo. "
            "Vérifie ton lien et réessaie."
        )

    finally:

        # Supprimer le fichier après utilisation
        if video_path and video_path.exists():
            video_path.unlink()


# 6. Fonction principale
def main():

    if not TOKEN:
        raise ValueError("Le token Telegram est absent du fichier .env")

    app = Application.builder().token(TOKEN).build()

    # Enregistrer les commandes
    app.add_handler(CommandHandler("start", start))

    # Recevoir les liens
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_link
        )
    )

    print("Bot démarré...")

    app.run_polling()


# 7. Lancer le programme
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    main()
