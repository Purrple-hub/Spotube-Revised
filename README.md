---

# Spotube-Revised

A modular Spotify MP3 downloader with a Flask web interface, streaming downloads, and memory‑aware concurrency.

> ⚠️ **Important**: This project requires valid **Spotify API credentials** to fetch track metadata. It does **not** scrape MP3s directly from Spotify – you'll need to plug in a real MP3 source (e.g., `yt‑dlp` or a third‑party downloader API).

---

## Features

- **Modular design** – core logic (`Spotube.py`), memory helpers (`Spo_Memory.py`), and a Flask web UI (`Spo_Fast.py`) are separated.
- **Streaming downloads** – writes MP3 files in chunks to avoid loading entire files into RAM.
- **Concurrency control** – a semaphore limits simultaneous downloads so you don't overwhelm your system.
- **Logging & reporting** – automatic log files and a reporter that collects them into a single report.
- **ZIP archiving** – package downloaded files and metadata into a compressed archive.
- **Web interface** – a simple Flask server to trigger downloads from your browser.

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Purrple-hub/Spotube-Revised.git
   cd Spotube-Revised
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt   # create this if you don't have one
   ```
   Key dependencies: `flask`, `aiohttp`, `curl_cffi`, `lxml`, `pandas`, `orjson`.

3. Configure your **Spotify API credentials** in `config.txt` (or via environment variables).

---

## Usage

Run the Flask server:
```bash
python main.py
```

Then open `http://localhost:5000` (or the port shown) and enter a Spotify playlist URL.

To use the CLI scraper directly:
```python
from Spotube import spotify_handling
df, manifest = spotify_handling("https://open.spotify.com/playlist/...")
```

---

## What's inside

- `Spotube.py` – scraping logic, downloader, data manipulation, error handlers.
- `Spo_Memory.py` – streaming download, concurrency semaphore, memory helpers.
- `Spo_Fast.py` – Flask web server, routes, security headers.
- `main.py` – entry point that starts the server.
- `templates/` – HTML templates for the web UI.
- `config.txt` – placeholder for your API keys.

---

## Status

This is a **work in progress**. The core scraper currently expects direct MP3 links – you'll need to integrate a real MP3 source (like `yt‑dlp` or a public downloader API) to make it fully functional. Pull requests welcome!

---

## License

MIT – see [LICENSE](LICENSE).
