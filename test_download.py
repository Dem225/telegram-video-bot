
from yt_dlp import YoutubeDL

url = "https://youtu.be/7wXJtQ5zGN0?si=31bBt8JxxzUx4Pyn"

options = {
    "format": "bestvideo*+bestaudio/best",
    "outtmpl": "video.%(ext)s",
    "merge_output_format": "mp4"
}

with YoutubeDL(options) as ydl:
    ydl.download([url])
