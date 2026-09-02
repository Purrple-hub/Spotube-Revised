import datetime
import logging
import os
import re
import zipfile as zp
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import orjson
import pandas as pd


LOGGER = logging.getLogger(__name__)
TRACK_COLUMNS = ["filename", "filepath", "size_bytes", "modified_at"]
def get_logging_files():
    # this function is used to get the logging files for the project, it will return a list of all the logging files in the current directory
    logging_files = []
    for file in os.listdir():
        if file.endswith(".log"):
            logging_files.append(file)
    return logging_files

def setup_logging():
    # this function is used to setup the logging for the project, it will create a logging file with the current date and time
    logging.basicConfig(filename=f"Spotube_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Logging setup complete.")

def is_spotify_url(url):
    try:
        parsed = urlparse(url)
    except (TypeError, ValueError):
        return False
    return (
        parsed.scheme in {"http", "https"}
        and parsed.netloc.lower() == "open.spotify.com"
        and parsed.path.split("/")[1:2] in [["track"], ["playlist"], ["album"]]
    )


def _spotify_client():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET before downloading.")
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
    except ImportError as exc:
        raise RuntimeError("Install dependencies from requirements.txt.") from exc
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    ))


def get_track_metadata(spotify_url):
    """Return metadata for a public Spotify track, playlist, or album."""
    if not is_spotify_url(spotify_url):
        raise ValueError("Expected a Spotify track, playlist, or album URL.")
    client = _spotify_client()
    resource_type, resource_id = urlparse(spotify_url).path.strip("/").split("/")[:2]
    if resource_type == "track":
        return [client.track(resource_id)]
    if resource_type == "album":
        return client.album_tracks(resource_id)["items"]
    tracks = []
    results = client.playlist_items(resource_id, fields="items(track(name,artists(name))),next")
    while results:
        tracks.extend(item["track"] for item in results["items"] if item.get("track"))
        results = client.next(results) if results.get("next") else None
    return tracks


def _safe_filename(value):
    return re.sub(r"[<>:\"/\\|?*]+", "_", value).strip(" .") or "track"


def _download_track(track, output_dir):
    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError("Install dependencies from requirements.txt.") from exc
    artists = ", ".join(artist["name"] for artist in track.get("artists", []))
    title = track.get("name", "Unknown track")
    filename = _safe_filename(f"{artists} - {title}")
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(output_dir) / f"{filename}.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with YoutubeDL(options) as downloader:
        downloader.download([f"ytsearch1:{artists} - {title} audio"])
    return str(Path(output_dir) / f"{filename}.mp3")

def data_manipulation(data):
    # data manipulation function i guess?
    if data is None:
        return pd.DataFrame(columns=["filename", "filepath", "size_bytes", "modified_at"])

    rows = []
    for filepath in data:
        if not filepath:
            continue
        filepath = os.path.abspath(os.path.expanduser(os.fspath(filepath)))
        try:
            stat = os.stat(filepath)
        except OSError as exc:
            logging.warning("Unable to inspect downloaded file %s: %s", filepath, exc)
            continue
        rows.append({
            "filename": os.path.basename(filepath),
            "filepath": filepath,
            "size_bytes": stat.st_size,
            "modified_at": datetime.datetime.fromtimestamp(
                stat.st_mtime
            ).isoformat(timespec="seconds"),
        })

    return pd.DataFrame(
        rows,
        columns=["filename", "filepath", "size_bytes", "modified_at"],
    )

def download_mp3(tracks, output_dir="Spotube_Downloads"):
    """Resolve Spotify metadata on YouTube and save authorized audio as MP3."""
    output_path = Path(output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    if not tracks:
        return []
    with ThreadPoolExecutor(max_workers=min(4, len(tracks))) as executor:
        return list(executor.map(lambda track: _download_track(track, output_path), tracks))

def start_scraping(spotify_url, output_dir="Spotube_Downloads"):
    setup_logging()
    tracks = get_track_metadata(spotify_url)
    downloaded_files = download_mp3(tracks, output_dir)
    df = data_manipulation(downloaded_files)
    return df
def save_manifest(output_dir="Spotube_Downloads"):
    scraping_files = get_logging_files()
    output_dir = os.path.abspath(os.path.expanduser(output_dir))
    os.makedirs(output_dir, exist_ok=True)
    manifest = {
        "finished_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "log_files": scraping_files,
    }
    manifest_path = os.path.join(output_dir, "scraping_manifest.json")
    with open(manifest_path, "wb") as manifest_file:
        manifest_file.write(orjson.dumps(manifest, option=orjson.OPT_INDENT_2))
    logging.info("Scraping manifest saved to: %s", manifest_path)
    return manifest_path


def finish_scraping_and_idk(output_dir="Spotube_Downloads"):
    """Backward-compatible alias for save_manifest."""
    return save_manifest(output_dir)
def spotify_handling(spotify_url, output_dir="Spotube_Downloads"):
    df = start_scraping(spotify_url, output_dir)
    manifest_path = save_manifest(output_dir)
    return df, manifest_path
# here im supposed to do all the wrok, fuccccccck
# i guess i can start with... i dunnoo? maybe. uh... forgot. okay maybe error handling?
def errors(operation="operation", default=None):
    try:
        if not callable(operation):
            raise TypeError("operation must be callable")
        return operation()
    except Exception as exc:
        logging.error("Operation failed: %s", exc)
    return default
# okay i finished it, god damn it.
# okay maybe what now...? uh maybe memory optimization? uh, no too hard, maybe something simpler? well. instead of storing everything in memory i can try in a simple compressed zip file called Data or some shit, i dunno
def save_to_zip(data, zip_filename="Data.zip"):
    zip_path = Path(zip_filename).expanduser().resolve()
    with zp.ZipFile(zip_path, 'w', zp.ZIP_DEFLATED) as archive:
        for index, item in enumerate(data):
            archive.writestr(f"item_{index}.json", orjson.dumps(item))
    logging.info("Data saved to zip file: %s", zip_path)
    return str(zip_path)
# okay? its... not bad, i hope so?
def loading_zips(zip_filename="Data.zip"):
    zip_path = Path(zip_filename).expanduser().resolve()
    if not zip_path.exists():
        logging.warning("Zip file does not exist: %s", zip_filename)
        return []
    with zp.ZipFile(zip_path, 'r') as archive:
        data = [orjson.loads(archive.read(name)) for name in archive.namelist()]
    logging.info("Data loaded from zip file: %s", zip_filename)
    return data
# ky let's try reporter for reports ig? uh. fuck.
def reporter():
    report_data = []

    for log_file in get_logging_files():
        if log_file == "reports.log":
            continue

        with open(log_file, "r", encoding="utf-8") as file:
            report_data.append({
                "log_file": log_file,
                "content": file.read(),
            })

    report_filename = "reports.log"
    report_content = orjson.dumps(report_data, option=orjson.OPT_INDENT_2)
    with open(report_filename, "wb") as file:
        file.write(report_content)

    logging.info("Report generated: %s", report_filename)
    return report_filename
# scraper errors? maybe i can think of something, for example if it fails on curl-cffi it can try using aiohttp instead.
scraper_errors = errors