from io import StringIO

from reconcile.sources import load_counts, load_price_feed, supplier_dirs

FEED = """<?xml version="1.0"?>
<catalogue>
  <item currency="EUR"><sku> a1 </sku><description>Bolt M6</description><price>0.50</price></item>
  <item currency="USD"><sku>b2</sku><description>Nut M6</description><price>0.10</price></item>
  <item><sku>c3</sku><description>Washer</description></item>
</catalogue>
"""


def test_price_feed(tmp_path):
    path = tmp_path / "prices.xml"
    path.write_text(FEED)
    frame = load_price_feed(path)
    assert list(frame["sku"]) == ["A1", "B2", "C3"]
    assert frame.loc[1, "currency"] == "USD"
    assert frame["unit_price"].isna().sum() == 1


def test_counts_are_summed_per_sku():
    csv = StringIO("sku,quantity,counted_at\na1,4,2026-09-01\nA1,6,2026-09-02\nb2,1,2026-09-01\n")
    frame = load_counts(csv).set_index("sku")
    assert frame.loc["A1", "counted"] == 10
    assert str(frame.loc["A1", "counted_at"].date()) == "2026-09-02"


def test_supplier_dirs(tmp_path):
    (tmp_path / "acme").mkdir()
    (tmp_path / "acme" / "stock.parquet").write_bytes(b"")
    (tmp_path / "empty").mkdir()
    assert [p.name for p in supplier_dirs(tmp_path)] == ["acme"]
