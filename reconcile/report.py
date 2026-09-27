from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape

_env = Environment(
    loader=PackageLoader("reconcile", "templates"),
    autoescape=select_autoescape(["html", "j2"]),
)


def _highlight(status):
    return "color: #b00020; font-weight: bold" if status == "mismatch" else ""


def _styled(frame):
    return (
        frame.style.format(
            {"variance": "{:.1%}", "unit_price": "{:,.2f}", "value_at_risk": "{:,.2f}"},
            na_rep="",
            escape="html",
        )
        .hide(axis="index")
        .map(_highlight, subset=["status"])
    )


def write_html(supplier, frame, summary, outdir):
    template = _env.get_template("summary.html.j2")
    html = template.render(
        supplier=supplier,
        generated=datetime.now(timezone.utc),
        summary=summary.to_dict("records"),
        table=_styled(frame).to_html(),
    )
    path = Path(outdir) / f"{supplier}-reconciliation.html"
    path.write_text(html, encoding="utf-8")
    return path


def write_excel(supplier, frame, summary, outdir):
    path = Path(outdir) / f"{supplier}-reconciliation.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        frame.to_excel(writer, sheet_name="Items", index=False)
    return path
