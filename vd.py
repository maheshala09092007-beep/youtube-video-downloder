import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp


# ============================================================
# CONFIGURATION
# ============================================================

DOWNLOAD_DIR = Path.home() / "Downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Browser to read YouTube/Instagram login cookies from.
# Options: "firefox", "chrome", "chromium", "brave", "edge" or None to disable.
# You must be logged in to YouTube in that browser.
COOKIE_BROWSER = "firefox"

# Menu choice -> max height (None = best available)
RESOLUTIONS = {
    "1": 2160,
    "2": 1440,
    "3": 1080,
    "4": 720,
    "5": 480,
    "6": 360,
    "7": None,
}

AUDIO_QUALITIES = {
    "1": "320",
    "2": "192",
    "3": "128",
}


# ============================================================
# PROGRESS HOOK
# ============================================================

def progress_hook(d):
    """Display download progress."""

    status = d.get("status")

    if status == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        speed = d.get("speed")
        eta = d.get("eta")

        if total:
            percentage = downloaded / total * 100
            speed_text = f"{speed / 1024 / 1024:.2f} MB/s" if speed else ""
            eta_text = f"ETA {eta}s" if eta is not None else ""

            print(
                f"\rDownloading: {percentage:6.2f}%"
                f" | {speed_text:<12}"
                f" | {eta_text:<10}",
                end="",
                flush=True,
            )
        else:
            print(
                f"\rDownloading: {downloaded / 1024 / 1024:.2f} MB",
                end="",
                flush=True,
            )

    elif status == "finished":
        print("\n[+] Download finished. Processing...")


# ============================================================
# HELPERS
# ============================================================

def is_valid_url(url):
    """Basic URL validation."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def ask_choice(prompt, options, default):
    """Ask until the user enters a valid option (Enter = default)."""
    while True:
        choice = input(prompt).strip() or default
        if choice in options:
            return choice
        print("[!] Invalid choice, try again.")


def ask_mode():
    print("\nWhat do you want to download?")
    print("  1) Video")
    print("  2) Audio only (MP3)")
    return ask_choice("Choose [1-2] (default 1): ", ("1", "2"), "1")


def ask_resolution():
    print("\nChoose max resolution:")
    print("  1) 2160p (4K)")
    print("  2) 1440p")
    print("  3) 1080p")
    print("  4) 720p")
    print("  5) 480p")
    print("  6) 360p")
    print("  7) Best available")
    choice = ask_choice("Choose [1-7] (default 3): ", RESOLUTIONS, "3")
    return RESOLUTIONS[choice]


def ask_audio_quality():
    print("\nChoose MP3 quality:")
    print("  1) 320 kbps")
    print("  2) 192 kbps")
    print("  3) 128 kbps")
    choice = ask_choice("Choose [1-3] (default 2): ", AUDIO_QUALITIES, "2")
    return AUDIO_QUALITIES[choice]


# ============================================================
# DOWNLOAD FUNCTION
# ============================================================

def build_options(mode, height=None, audio_quality="192"):
    """Build yt-dlp options for video or audio mode."""

    opts = {
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s [%(id)s].%(ext)s"),
        "noplaylist": True,
        "overwrites": False,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
        "retry_sleep_functions": {
            "http": lambda n: min(5 * n, 30),
            "fragment": lambda n: min(5 * n, 30),
        },
        "windowsfilenames": True,
        "restrictfilenames": False,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": False,
        "socket_timeout": 30,
        "keepvideo": False,
    }

    # Login cookies help avoid "Sign in to confirm you're not a bot"
    if COOKIE_BROWSER:
        opts["cookiesfrombrowser"] = (COOKIE_BROWSER,)

    # YouTube needs a JavaScript runtime. deno is used by default;
    # fall back to node if deno isn't installed.
    if not shutil.which("deno") and shutil.which("node"):
        opts["js_runtimes"] = {"node": {}}

    if mode == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_quality,
            }
        ]
    else:
        if height:
            # Best video up to chosen height + best audio,
            # fall back to a single combined file if needed
            opts["format"] = (
                f"bv*[height<={height}]+ba/b[height<={height}]/b"
            )
        else:
            opts["format"] = "bv*+ba/b"
        opts["merge_output_format"] = "mp4"

    return opts


def download(url, mode, height=None, audio_quality="192"):
    """Download video or audio using yt-dlp."""

    ydl_opts = build_options(mode, height, audio_quality)

    try:
        print("\n==========================================")
        print("        YT-DLP DOWNLOADER")
        print("==========================================")
        print(f"\nURL   : {url}")
        print(f"Mode  : {'Audio (MP3)' if mode == 'audio' else 'Video'}")
        if mode == "video":
            print(f"Max   : {str(height) + 'p' if height else 'Best'}")
        print(f"Output: {DOWNLOAD_DIR}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown")
            video_id = info.get("id", "Unknown")

        print("\n==========================================")
        print("          DOWNLOAD COMPLETE")
        print("==========================================")
        print(f"Title : {title}")
        print(f"ID    : {video_id}")
        print(f"Folder: {DOWNLOAD_DIR}")
        return True

    except KeyboardInterrupt:
        print("\n\n[!] Download cancelled by user.")
        return False

    except yt_dlp.utils.DownloadError as e:
        print("\n\n==========================================")
        print("          DOWNLOAD ERROR")
        print("==========================================")
        print(f"{e}")
        return False

    except Exception as e:
        print("\n\n==========================================")
        print("          UNEXPECTED ERROR")
        print("==========================================")
        print(f"{type(e).__name__}: {e}")
        return False


# ============================================================
# MAIN
# ============================================================

def main():
    print("==========================================")
    print("        VIDEO / AUDIO DOWNLOADER")
    print("==========================================")

    url = input("\nlink kottu bro: ").strip()

    if not url:
        print("\n[!] No URL entered.")
        sys.exit(1)

    if not is_valid_url(url):
        print("\n[!] Invalid URL.")
        sys.exit(1)

    mode = "audio" if ask_mode() == "2" else "video"

    if mode == "audio":
        success = download(url, "audio", audio_quality=ask_audio_quality())
    else:
        success = download(url, "video", height=ask_resolution())

    if success:
        print("\n[+] Done.")
    else:
        print("\n[-] Download failed.")


if __name__ == "__main__":
    main()
