from pathlib import Path

import pandas as pd
from lxml import etree

STOCK_COLUMNS = ["sku", "on_hand", "reserved", "updated_at"]
PRICE_COLUMNS = ["sku", "description", "unit_price", "currency"]


def supplier_dirs(inbox):
    inbox = Path(inbox)
    if not inbox.is_dir():
        return []
    return sorted(p for p in inbox.iterdir() if p.is_dir() and (p / "stock.parquet").exists())


def load_supplier_stock(path):
    frame = pd.read_parquet(path, engine="pyarrow", columns=STOCK_COLUMNS)
    frame["sku"] = frame["sku"].astype("string").str.strip().str.upper()
    frame["updated_at"] = pd.to_datetime(frame["updated_at"], utc=True)
    frame["available"] = (frame["on_hand"] - frame["reserved"]).clip(lower=0)
    return frame


def empty_price_feed():
    return pd.DataFrame(columns=PRICE_COLUMNS)


def load_price_feed(path):
    rows = []
    for _, elem in etree.iterparse(str(path), events=("end",), tag="item"):
        price = elem.findtext("price")
        rows.append(
            {
                "sku": (elem.findtext("sku") or "").strip().upper(),
                "description": (elem.findtext("description") or "").strip(),
                "unit_price": float(price) if price else float("nan"),
                "currency": elem.get("currency", "EUR"),
            }
        )
        elem.clear()
    if not rows:
        return empty_price_feed()
    return pd.DataFrame(rows, columns=PRICE_COLUMNS).drop_duplicates("sku", keep="last")


def load_counts(path_or_buffer):
    frame = pd.read_csv(path_or_buffer, dtype={"sku": "string"}, parse_dates=["counted_at"])
    frame["sku"] = frame["sku"].str.strip().str.upper()
    return frame.groupby("sku", as_index=False).agg(
        counted=("quantity", "sum"), counted_at=("counted_at", "max")
    )
