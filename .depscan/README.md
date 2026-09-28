# depscan-heldout-4 answer key

pandas batch job (`stockcheck`) that reads supplier Parquet/XML drops, downloads manifest
attachments with requests, and renders HTML/Excel reports. OSV returns 7 distinct advisories across
all pins (`requirements.txt` + `requirements-dev.txt`); all 7 are labelled. 2 likely_affected,
4 likely_not_affected, 1 uncertain.

| advisory | package | expected | why |
|---|---|---|---|
| CVE-2023-47248 | pyarrow 14.0.0 | likely_affected (reachable_via_framework) | `pd.read_parquet(..., engine="pyarrow")` on supplier-supplied `stock.parquet` (`reconcile/sources.py:18`); pyarrow is reached only through pandas. |
| CVE-2024-52338 | pyarrow 14.0.0 | likely_not_affected (api_not_used) | Advisory covers the Arrow **R** package only; no R in this project. |
| CVE-2026-41066 | lxml 5.3.0 | likely_affected (reachable_untrusted_input) | `etree.iterparse()` with default `resolve_entities` on each supplier's `prices.xml` (`reconcile/sources.py:31`); entity-expanded text flows into the reports. |
| CVE-2025-27516 | jinja2 3.1.5 | likely_not_affected (constant_input) | Sandbox breakout needs attacker-controlled template source in a sandbox; only the packaged `summary.html.j2` is rendered, with a normal `Environment` (`reconcile/report.py:7,30`). |
| CVE-2024-47081 | requests 2.32.3 | uncertain (was likely_affected) (reachable_untrusted_input) | `fetch_attachments()` GETs URLs taken from supplier `manifest.json` with a default Session (trust_env on, no auth) on a host with `~/.netrc` (`reconcile/fetch.py:35`). Uncertain because impact requires a .netrc on the host at run time, which is documented in the README but not visible in the code. |
| CVE-2026-25645 | requests 2.32.3 | likely_not_affected (api_not_used) | Only direct callers of `requests.utils.extract_zipped_paths()` are affected; the code uses `Session.get` only. |
| CVE-2024-34062 | tqdm 4.66.2 (dev) | likely_not_affected (dev_only) | Vulnerable path is tqdm's CLI option parsing; tqdm is a dev requirement used only as `tqdm(iterable)` in `scripts/backfill.py:23`. |

Notes
- The pyarrow site is the `read_parquet(engine="pyarrow")` call, since pyarrow is never imported.
- Pins with no OSV advisories: pandas 2.2.3, numpy 1.26.4, openpyxl 3.1.5, et-xmlfile, markupsafe, python-dateutil,
  pytz, six, tzdata, urllib3 2.8.0, idna 3.20, certifi, charset-normalizer, and the pytest toolchain.
- CVE-2024-47081 depends on a `.netrc` being present; the project README documents that the service account uses one.
