import numpy as np
import pandas as pd

STATUS_ORDER = ["mismatch", "not_counted", "unknown_to_supplier", "ok"]


def reconcile(stock, counts, prices, threshold):
    known = set(stock["sku"]) | set(prices["sku"])
    counts = counts[counts["sku"].isin(known)]
    merged = stock.merge(counts, on="sku", how="outer", indicator=True)
    merged = merged.merge(prices, on="sku", how="left")
    merged["available"] = merged["available"].fillna(0)
    merged["counted"] = merged["counted"].fillna(0)
    merged["difference"] = merged["counted"] - merged["available"]
    ratio = merged["difference"].abs() / merged["available"].where(merged["available"] > 0)
    merged["variance"] = np.where(
        merged["available"] > 0, ratio, (merged["difference"] != 0).astype(float)
    )
    merged["value_at_risk"] = (merged["difference"].abs() * merged["unit_price"]).round(2)
    merged["status"] = np.select(
        [
            merged["_merge"] == "left_only",
            merged["_merge"] == "right_only",
            merged["variance"] > threshold,
        ],
        ["not_counted", "unknown_to_supplier", "mismatch"],
        default="ok",
    )
    merged["status"] = pd.Categorical(merged["status"], categories=STATUS_ORDER, ordered=True)
    columns = [
        "sku", "description", "available", "counted", "difference",
        "variance", "unit_price", "currency", "value_at_risk", "status",
    ]
    return merged[columns].sort_values(["status", "value_at_risk"], ascending=[True, False]).reset_index(drop=True)


def summarise(frame):
    summary = frame.groupby("status", observed=False).agg(
        items=("sku", "count"), value_at_risk=("value_at_risk", "sum")
    )
    return summary.reset_index()
