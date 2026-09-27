import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_COUNTS_URL = "https://files.warehouse.internal/counts/latest.csv"


@dataclass(frozen=True)
class Settings:
    inbox: Path
    outdir: Path
    counts_url: str
    variance_threshold: float = 0.05
    timeout: int = 30


def load_settings(inbox=None, outdir=None):
    return Settings(
        inbox=Path(inbox or os.environ.get("STOCKCHECK_INBOX", "inbox")),
        outdir=Path(outdir or os.environ.get("STOCKCHECK_OUTDIR", "out")),
        counts_url=os.environ.get("STOCKCHECK_COUNTS_URL", DEFAULT_COUNTS_URL),
        variance_threshold=float(os.environ.get("STOCKCHECK_THRESHOLD", "0.05")),
        timeout=int(os.environ.get("STOCKCHECK_TIMEOUT", "30")),
    )
