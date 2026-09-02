# memory handling but its made by Deepseek cuz im fucking lazy

import os
import threading
from urllib.parse import unquote, urlparse
import curl_cffi
def stream_download(link, output_dir, chunk_size=8192):
    """Download MP3 in chunks, writing directly to file."""
    filename = os.path.basename(unquote(urlparse(link).path)) or "download.mp3"
    filepath = os.path.join(output_dir, filename)
    with curl_cffi.requests.get(link, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    return filepath
_semaphore = threading.Semaphore(8)   # default max workers

def set_concurrency(limit):
    """Change the max number of concurrent downloads."""
    global _semaphore
    _semaphore = threading.Semaphore(limit)
def limited_download(link, output_dir):
    """Download with streaming + concurrency control."""
    with _semaphore:
        return stream_download(link, output_dir)