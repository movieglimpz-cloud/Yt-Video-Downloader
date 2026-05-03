"""
YouTube Video Downloader - Context Menu Script
Usage: python yt_download.py "FOLDER_PATH"
Reads YouTube URL from clipboard automatically.
"""

import subprocess
import sys
import os
import re
import ctypes


def show_popup(title, message, icon=0x40):
    """Show a Windows message box. icon: 0x40=info, 0x10=error"""
    ctypes.windll.user32.MessageBoxW(0, message, title, icon)


def get_clipboard_url():
    """Read text from Windows clipboard."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get().strip()
        root.destroy()
        return text
    except Exception:
        return None


def is_youtube_url(url):
    """Check if the URL looks like a valid YouTube link."""
    pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+'
    return bool(re.match(pattern, url))


def main():
    # --- Get the target folder ---
    if len(sys.argv) < 2:
        show_popup("YT Downloader", "No folder path provided.\nRight-click a folder to use this tool.", 0x10)
        sys.exit(1)

    folder = sys.argv[1].strip('"').strip("'")

    if not os.path.isdir(folder):
        show_popup("YT Downloader ❌", f"Folder not found:\n{folder}", 0x10)
        sys.exit(1)

    # --- Get URL from clipboard ---
    url = get_clipboard_url()

    if not url:
        show_popup("YT Downloader ❌", "Clipboard is empty.\nCopy a YouTube URL first, then right-click the folder.", 0x10)
        sys.exit(1)

    if not is_youtube_url(url):
        show_popup(
            "YT Downloader ❌",
            f"The clipboard doesn't contain a valid YouTube URL.\n\nFound:\n{url[:100]}",
            0x10
        )
        sys.exit(1)

    # --- Build yt-dlp command ---
    output_template = os.path.join(folder, "%(title)s.%(ext)s")

    # Use cookies.txt sitting next to this script (no need to close Chrome!)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_file = os.path.join(script_dir, "cookies.txt")

    if os.path.exists(cookies_file):
        cookies_arg = ["--cookies", cookies_file]
    else:
        cookies_arg = ["--cookies-from-browser", "chrome"]

    cmd = [
        "yt-dlp",
        "--remote-components", "ejs:github",
        # Download best video + best audio separately, re-encode audio to aac so it's always compatible
        "--format", "bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "--postprocessor-args", "ffmpeg:-c:v copy -c:a aac -b:a 192k",
        "--output", output_template,
        "--no-playlist",
        "--retries", "3",
        "--fragment-retries", "3",
    ] + cookies_arg + [url]

    # --- Show "starting" notice ---
    show_popup(
        "YT Downloader ⏳",
        f"Download started!\n\nURL: {url[:60]}...\nSaving to: {folder}\n\nYou'll get a notification when it's done.",
        0x40
    )

    # --- Run yt-dlp ---
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode == 0:
            filename = ""
            for line in result.stdout.splitlines():
                m = re.search(r'\[(?:download|Merger)\].*Destination:\s+(.+)', line)
                if m:
                    filename = os.path.basename(m.group(1))

            msg = f"✅ Download complete!\n\nSaved to:\n{folder}"
            if filename:
                msg += f"\n\nFile: {filename}"
            show_popup("YT Downloader ✅", msg, 0x40)

        else:
            stderr = result.stderr + result.stdout
            hint = ""
            if "Sign in" in stderr or "bot" in stderr.lower():
                hint = "\n\n💡 Tip: Re-export cookies.txt from Chrome\nusing the 'Get cookies.txt LOCALLY' extension."
            elif "ffmpeg" in stderr.lower():
                hint = "\n\n💡 Tip: ffmpeg not found. Make sure it's installed."
            elif "cookies" in stderr.lower():
                hint = "\n\n💡 Tip: cookies.txt may be expired.\nRe-export it from Chrome."

            show_popup(
                "YT Downloader ❌",
                f"Download failed (code {result.returncode}){hint}\n\nError:\n{stderr[-300:]}",
                0x10
            )

    except FileNotFoundError:
        show_popup(
            "YT Downloader ❌",
            "yt-dlp was not found.\n\nInstall it:\n  pip install yt-dlp",
            0x10
        )


if __name__ == "__main__":
    main()