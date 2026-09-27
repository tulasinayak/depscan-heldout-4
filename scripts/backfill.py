"""Re-run the reconciliation over archived inbox snapshots (one folder per day).

    python -m scripts.backfill archive/2026-08 --out out/backfill
"""
import argparse
import logging
from pathlib import Path

from tqdm import tqdm

from reconcile.cli import run
from reconcile.config import load_settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/backfill"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)
    snapshots = sorted(p for p in args.archive.iterdir() if p.is_dir())
    total = 0
    for snapshot in tqdm(snapshots, desc="snapshots", unit="day"):
        total += len(run(load_settings(snapshot, args.out / snapshot.name)))
    print(f"{len(snapshots)} snapshots, {total} files")


if __name__ == "__main__":
    main()
