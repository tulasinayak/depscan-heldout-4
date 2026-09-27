import argparse
import logging
import sys

from .config import load_settings
from .fetch import fetch_attachments, fetch_counts
from .report import write_excel, write_html
from .sources import (
    empty_price_feed,
    load_counts,
    load_price_feed,
    load_supplier_stock,
    supplier_dirs,
)
from .transform import reconcile, summarise

log = logging.getLogger("reconcile")


def run(settings):
    settings.outdir.mkdir(parents=True, exist_ok=True)
    counts = load_counts(fetch_counts(settings.counts_url, settings.timeout))
    written = []
    for folder in supplier_dirs(settings.inbox):
        supplier = folder.name
        stock = load_supplier_stock(folder / "stock.parquet")
        prices_path = folder / "prices.xml"
        prices = load_price_feed(prices_path) if prices_path.exists() else empty_price_feed()
        attachments = fetch_attachments(folder, settings.timeout)
        result = reconcile(stock, counts, prices, settings.variance_threshold)
        summary = summarise(result)
        written.append(write_html(supplier, result, summary, settings.outdir))
        written.append(write_excel(supplier, result, summary, settings.outdir))
        mismatches = int((result["status"] == "mismatch").sum())
        log.info("%s: %d items, %d mismatches, %d attachments", supplier, len(result), mismatches, len(attachments))
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="stockcheck", description="Reconcile supplier stock files against warehouse counts."
    )
    parser.add_argument("--inbox", help="directory with one sub-folder per supplier")
    parser.add_argument("--out", help="directory for the generated reports")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    files = run(load_settings(args.inbox, args.out))
    print(f"wrote {len(files)} report files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
