import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys

# Attempt to install required packages if they are not installed
required_modules = ["yt-dlp", "ttkbootstrap"]
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"Module {module} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

from yt_dlp import YoutubeDL
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Use user's home directory to save config.json to avoid permission issues
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, "config.json")

# Load or initialize the download directory
def get_download_directory():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("download_directory", "")
    return ""

def save_download_directory(directory):
    # Save config to user's home directory to avoid permission issues
    with open(CONFIG_FILE, "w") as f:
        json.dump({"download_directory": directory}, f)

# Function to set the download directory
def set_download_directory():
    directory = filedialog.askdirectory(title="Select Download Directory")
    if directory:
        save_download_directory(directory)
        download_dir_var.set(directory)
        messagebox.showinfo("Directory Set", f"Download directory set to:\n{directory}")

# Function to download a single video or playlist
def download_url(url, download_directory, progress_callback):
    options = {
        "outtmpl": os.path.join(download_directory, "%(playlist_title)s", "%(title)s.%(ext)s"),
        "format": "best",
        "progress_hooks": [progress_callback],
    }
    with YoutubeDL(options) as ydl:
        ydl.download([url])

# Threaded download function to avoid GUI freezing
def start_download():
    download_directory = download_dir_var.get()
    urls = url_text.get("1.0", "end").strip().splitlines()
    
    if not urls:
        messagebox.showerror("Error", "Please enter one or more YouTube URLs.")
        return
    
    if not download_directory.strip():
        messagebox.showerror("Error", "Please set a download directory first.")
        return

    def download_task():
        for index, url in enumerate(urls, start=1):
            progress_var.set(0)  # Reset progress bar
            status_var.set(f"Downloading ({index}/{len(urls)}): {url}")
            try:
                download_url(url, download_directory, progress_hook)
                status_var.set(f"Completed ({index}/{len(urls)}): {url}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download {url}:\n{str(e)}")

        status_var.set("All downloads complete!")
        progress_var.set(100)

    threading.Thread(target=download_task, daemon=True).start()

# Progress hook for yt_dlp
def progress_hook(d):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes", 1)
        progress = int(downloaded / total * 100)
        progress_var.set(progress)

# Initialize the GUI application
app = ttk.Window(themename="superhero")
app.title("YouTube Video Downloader")
app.geometry("600x650")

# Download directory
download_dir_var = ttk.StringVar(value=get_download_directory())

# Header Label
header_label = ttk.Label(app, text="Welcome to YouTube Video Downloader", font=("Arial", 16, "bold"), anchor="center", bootstyle=DANGER)
header_label.pack(pady=10)

# Download directory section
ttk.Label(app, text="Download Directory:", font=("Arial", 12)).pack(pady=5)
ttk.Entry(app, textvariable=download_dir_var, font=("Arial", 12), state="readonly", width=50).pack(pady=5)
ttk.Button(app, text="Set Download Directory", command=set_download_directory, bootstyle=SUCCESS).pack(pady=5)

# YouTube URL input section
ttk.Label(app, text="YouTube Video/Playlist URLs (one per line):", font=("Arial", 12)).pack(pady=10)
url_text = tk.Text(app, font=("Arial", 12), height=8, width=60)
url_text.pack(pady=5)

# Informational Text
info_label = ttk.Label(app, text="This tool works best for downloading full playlists. It will work for single videos too!", font=("Arial", 10), anchor="center", bootstyle=INFO)
info_label.pack(pady=10)

# Status and progress bar
status_var = ttk.StringVar(value="Idle")
ttk.Label(app, textvariable=status_var, font=("Arial", 10), foreground="blue").pack(pady=5)

progress_var = ttk.IntVar(value=0)
progress_bar = ttk.Progressbar(app, orient="horizontal", length=500, mode="determinate", variable=progress_var, bootstyle=INFO)
progress_bar.pack(pady=5)

# Download button
ttk.Button(app, text="Download", command=start_download, bootstyle="primary").pack(pady=20)

# Start the application
app.mainloop()
