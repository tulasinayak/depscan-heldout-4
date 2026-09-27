import json
import logging
from io import StringIO
from pathlib import Path
from urllib.parse import urlsplit

import requests

from . import __version__

log = logging.getLogger(__name__)

_session = requests.Session()
_session.headers["User-Agent"] = f"stockcheck/{__version__}"


def fetch_counts(url, timeout=30):
    response = _session.get(url, timeout=timeout)
    response.raise_for_status()
    return StringIO(response.text)


def fetch_attachments(supplier_dir, timeout=30):
    manifest_path = Path(supplier_dir) / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = Path(supplier_dir) / "attachments"
    target.mkdir(exist_ok=True)
    saved = []
    for entry in manifest.get("attachments", []):
        url = entry["url"]
        name = Path(urlsplit(url).path).name or "attachment"
        try:
            response = _session.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            log.warning("could not fetch %s: %s", url, exc)
            continue
        dest = target / name
        dest.write_bytes(response.content)
        saved.append(dest)
    return saved
