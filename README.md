# Spotube-Revised

A modular, memory‑aware Spotify MP3 downloader with a Flask web interface – because downloading playlists shouldn't crash your laptop.

## What the hell is this?

I wanted a tool that scrapes Spotify playlists and downloads the MP3s without eating all my RAM. So I built this mess. It's split into three files:

- `Spotube.py` – the core scraping, downloading, and logging logic.
- `Spo_Memory.py` – streaming downloads and concurrency control (so you don't spawn 1000 threads).
- `Spo_Fast.py` – a simple Flask server to trigger downloads from your browser.

I also added a few helpers: ZIP archiving, error handlers (that I barely use), and a reporter that collects logs.

## Does it actually work?

**Kinda.** The downloader works – if you give it a direct MP3 link, it'll stream and save it with a semaphore to limit concurrency. But the big catch is: **Spotify doesn't give you MP3 links.** My current scraper scrapes the HTML for `<a href="...mp3">` – which doesn't exist. So by default, you get zero files.

You'll need to plug in a real MP3 source (e.g., `yt‑dlp`, `spotify‑downloader`, or a third‑party API) to make this actually useful. I'm working on it, but Python is kicking my ass.

## How to run it

1. Clone this repo:
   ```bash
   git clone https://github.com/Purrple-hub/Spotube-Revised.git
   cd Spotube-Revised
   ```
