from yt_dlp import YoutubeDL

url = input("Link kottu bro: ")

downloads_path = "/home/ala/Downloads/%(title)s.%(ext)s"

options = {
    "format": "bestaudio/best",
    "outtmpl": downloads_path,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

with YoutubeDL(options) as ydl:
    ydl.download([url])

print("\nDone! Audio saved to /home/ala/Downloads/")
