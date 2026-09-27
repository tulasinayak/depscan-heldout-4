# stockcheck

Nightly batch job that reconciles supplier stock files against our warehouse counts.

Each supplier has a folder in the inbox (synced from the partner SFTP drop):

```
inbox/
  acme/
    stock.parquet    # sku, on_hand, reserved, updated_at - exported by the supplier's ERP
    prices.xml       # the supplier's price feed (<item><sku/><description/><price/></item>)
    manifest.json    # optional: {"attachments": [{"url": "..."}]} - delivery notes etc.
```

The job downloads the latest warehouse count sheet from the internal file server, loads each
supplier's stock and price feed with pandas, flags SKUs whose counted quantity differs from the
supplier's available quantity by more than the threshold, and writes an HTML and an Excel report
per supplier to the output directory. Attachments listed in a supplier manifest are downloaded
next to the supplier's files for the buyers to review.

## Usage

```
pip install -r requirements.txt
python -m reconcile.cli --inbox /srv/stockcheck/inbox --out /srv/stockcheck/out
```

Configuration comes from environment variables: `STOCKCHECK_INBOX`, `STOCKCHECK_OUTDIR`,
`STOCKCHECK_COUNTS_URL`, `STOCKCHECK_THRESHOLD` (default 0.05) and `STOCKCHECK_TIMEOUT`.
Downloads authenticate against the warehouse file server with the service account's `~/.netrc`.

## Development

```
pip install -r requirements.txt -r requirements-dev.txt
pytest
python -m scripts.backfill archive/2026-08    # re-run archived daily snapshots
```

Runs on Python 3.12.
