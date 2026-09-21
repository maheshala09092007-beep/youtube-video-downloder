import os
from yt_dlp import YoutubeDL

url = input("link kottu bro: ")

# Explicitly targets your user's Downloads folder
downloads_path = "/home/ala/Downloads/%(title)s.%(ext)s"

options = {
    "format": "bv*+ba/b",
    "merge_output_format": "mp4",
    "outtmpl": downloads_path,
}

with YoutubeDL(options) as ydl:
    ydl.download([url])

print("\nDone! Video saved to /home/ala/Downloads/")
