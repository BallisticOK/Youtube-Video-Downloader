import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
from yt_dlp import YoutubeDL
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# User's home directory for config
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, "config.json")

# Install/update required packages
required_modules = ["yt-dlp", "ttkbootstrap"]
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"Installing missing module: {module}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# Load or save download directory
def get_download_directory():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("download_directory", "")
    return ""

def save_download_directory(directory):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"download_directory": directory}, f)

# Set download directory
def set_download_directory():
    directory = filedialog.askdirectory(title="Select Download Directory")
    if directory:
        save_download_directory(directory)
        download_dir_var.set(directory)
        messagebox.showinfo("Directory Set", f"Download directory set to:\n{directory}")

# Download video or audio
def download_url(url, download_directory, download_format, progress_callback):
    if download_format == "MP4":
        options = {
            "outtmpl": os.path.join(download_directory, "%(playlist_title)s", "%(title)s.%(ext)s"),
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "progress_hooks": [progress_callback],
            "retries": 3,
        }
    elif download_format == "MP3":
        options = {
            "outtmpl": os.path.join(download_directory, "%(playlist_title)s", "%(title)s.%(ext)s"),
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "progress_hooks": [progress_callback],
            "retries": 3,
        }
    else:
        raise ValueError("Invalid download format.")

    with YoutubeDL(options) as ydl:
        ydl.download([url])

def start_download():
    download_directory = download_dir_var.get()
    urls = url_text.get("1.0", "end").strip().splitlines()
    download_format = format_var.get()
    
    if not urls:
        messagebox.showerror("Error", "Please enter one or more YouTube URLs.")
        return
    if not download_directory.strip():
        messagebox.showerror("Error", "Please set a download directory first.")
        return

    def download_task():
        for index, url in enumerate(urls, start=1):
            progress_var.set(0)
            status_var.set(f"Downloading ({index}/{len(urls)}): {url}")
            try:
                download_url(url, download_directory, download_format, progress_hook)
                status_var.set(f"Completed ({index}/{len(urls)}): {url}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download {url}:\n{str(e)}")

        status_var.set("All downloads complete!")
        progress_var.set(100)

    threading.Thread(target=download_task, daemon=True).start()

# Progress hook
def progress_hook(d):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes", 1)
        if total > 0:
            progress = int(downloaded / total * 100)
            progress_var.set(progress)

# GUI
app = ttk.Window(themename="superhero")
app.title("YouTube Video Downloader")
app.geometry("600x700")

download_dir_var = ttk.StringVar(value=get_download_directory())
format_var = ttk.StringVar(value="MP4")  # Default to MP4

header_label = ttk.Label(app, text="Welcome to YouTube Video Downloader", font=("Arial", 16, "bold"), anchor="center", bootstyle=DANGER)
header_label.pack(pady=10)

ttk.Label(app, text="Download Directory:", font=("Arial", 12)).pack(pady=5)
ttk.Entry(app, textvariable=download_dir_var, font=("Arial", 12), state="readonly", width=50).pack(pady=5)
ttk.Button(app, text="Set Download Directory", command=set_download_directory, bootstyle=SUCCESS).pack(pady=5)

ttk.Label(app, text="YouTube Video/Playlist URLs (one per line):", font=("Arial", 12)).pack(pady=10)
url_text = tk.Text(app, font=("Arial", 12), height=8, width=60)
url_text.pack(pady=5)

# Format selection
ttk.Label(app, text="Select Download Format:", font=("Arial", 12)).pack(pady=10)
format_frame = ttk.Frame(app)
format_frame.pack(pady=5)
ttk.Radiobutton(format_frame, text="MP4 (Video)", value="MP4", variable=format_var, bootstyle="primary").grid(row=0, column=0, padx=10)
ttk.Radiobutton(format_frame, text="MP3 (Audio)", value="MP3", variable=format_var, bootstyle="success").grid(row=0, column=1, padx=10)

info_label = ttk.Label(app, text="This tool supports downloading videos as MP4 or audio as MP3.", font=("Arial", 10), anchor="center", bootstyle=INFO)
info_label.pack(pady=10)

status_var = ttk.StringVar(value="Idle")
ttk.Label(app, textvariable=status_var, font=("Arial", 10), foreground="blue").pack(pady=5)

progress_var = ttk.IntVar(value=0)
progress_bar = ttk.Progressbar(app, orient="horizontal", length=500, mode="determinate", variable=progress_var, bootstyle=INFO)
progress_bar.pack(pady=5)

ttk.Button(app, text="Download", command=start_download, bootstyle="primary").pack(pady=20)

app.mainloop()
