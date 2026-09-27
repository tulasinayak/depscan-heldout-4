import pandas as pd

from reconcile.transform import reconcile, summarise


def make_inputs():
    stock = pd.DataFrame(
        {"sku": ["A1", "B2", "C3"], "available": [10, 0, 5]}
    )
    counts = pd.DataFrame(
        {"sku": ["A1", "B2", "Z9"], "counted": [10, 3, 1], "counted_at": pd.to_datetime(["2026-09-01"] * 3)}
    )
    prices = pd.DataFrame(
        {"sku": ["A1", "B2", "C3"], "description": ["bolt", "nut", "washer"],
         "unit_price": [0.5, 0.1, 0.05], "currency": ["EUR"] * 3}
    )
    return stock, counts, prices


def test_statuses():
    result = reconcile(*make_inputs(), threshold=0.05)
    status = dict(zip(result["sku"], result["status"].astype(str)))
    assert status == {"A1": "ok", "B2": "mismatch", "C3": "not_counted"}


def test_counts_for_other_suppliers_are_ignored():
    result = reconcile(*make_inputs(), threshold=0.05)
    assert "Z9" not in set(result["sku"])


def test_value_at_risk():
    result = reconcile(*make_inputs(), threshold=0.05).set_index("sku")
    assert result.loc["B2", "value_at_risk"] == 0.3
    assert result.loc["C3", "value_at_risk"] == 0.25


def test_summary_has_all_statuses():
    summary = summarise(reconcile(*make_inputs(), threshold=0.05))
    assert list(summary["status"].astype(str)) == ["mismatch", "not_counted", "unknown_to_supplier", "ok"]
    assert summary["items"].sum() == 3
