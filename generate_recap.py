#!/usr/bin/env python3
"""Build the daily market recap page from Yahoo Finance daily data."""
import html
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

# DRAM is the Roundhill Memory ETF. The symbol is intentionally explicit so it
# is easy to replace independently if the data provider changes its symbol.
TICKERS = {
    "MU": "Micron Technology",
    "DRAM": "Roundhill Memory ETF",
    "MRVL": "Marvell Technology",
    "GDXU": "Gold Miners 2x",
    "NBIS": "Nebius Group",
}


def scalar(value):
    """Convert a pandas/numpy scalar or one-element Series to float."""
    if hasattr(value, "iloc"):
        value = value.iloc[0]
    return float(value)


def fmt(value):
    return "—" if value is None else f"${value:,.2f}"


def load_quote(symbol):
    """Return close, previous close, change and percentage for one symbol."""
    data = yf.download(
        symbol,
        period="5d",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if data.empty or "Close" not in data:
        raise RuntimeError(f"no daily close data returned for {symbol}")

    closes = data["Close"]
    if getattr(closes, "ndim", 1) > 1:
        closes = closes.iloc[:, 0]
    closes = closes.dropna()
    if closes.empty:
        raise RuntimeError(f"no valid daily close data returned for {symbol}")

    close = scalar(closes.iloc[-1])
    previous = scalar(closes.iloc[-2]) if len(closes) > 1 else None
    change = close - previous if previous is not None else None
    pct = change / previous * 100 if previous else None
    return close, change, pct


def main():
    cards = []
    rows = []
    failures = []

    for ticker, name in TICKERS.items():
        try:
            close, change, pct = load_quote(ticker)
        except Exception as exc:
            failures.append(f"{ticker}: {exc}")
            continue

        direction = "up" if (change or 0) >= 0 else "down"
        sign = "+" if (change or 0) >= 0 else ""
        change_text = f"{sign}{fmt(abs(change))}" if change is not None else "—"
        pct_text = f"{sign}{pct:.2f}%" if pct is not None else "—"
        safe_name = html.escape(name)
        cards.append(
            f'<article class="card {direction}"><div class="ticker">{ticker}'
            f'<span class="dot"></span></div><div class="name">{safe_name}</div>'
            f'<div class="price">{fmt(close)}</div><div class="change">{change_text} '
            f'<span>({pct_text})</span></div></article>'
        )
        rows.append(
            f"<tr><td><strong>{ticker}</strong><small>{safe_name}</small></td>"
            f"<td>{fmt(close)}</td><td class='{direction}'>{change_text}</td>"
            f"<td class='{direction}'>{pct_text}</td></tr>"
        )

    if not cards:
        raise RuntimeError("no market data was available: " + "; ".join(failures))

    warning = ""
    if failures:
        warning = "<p class=\"warning\">Unavailable: " + html.escape("; ".join(failures)) + "</p>"
    now = datetime.now(timezone.utc).strftime("%B %d, %Y · %H:%M UTC")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Market Recap</title><style>
:root{{--bg:#0a0d14;--panel:#111722;--line:#222b3c;--text:#f4f7fb;--muted:#8b96aa;--green:#45e0a2;--red:#ff6b82;--blue:#84a9ff;--warn:#ffd166}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 80% -10%,#1e2e55 0,transparent 35%),var(--bg);color:var(--text);font:15px Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}main{{max-width:1120px;margin:auto;padding:48px 24px 72px}}header{{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:42px}}h1{{font-size:clamp(2.4rem,6vw,5rem);line-height:.95;letter-spacing:-.07em;margin:8px 0 16px}}.eyebrow{{color:var(--blue);font-size:12px;font-weight:800;letter-spacing:.18em;text-transform:uppercase}}.sub,.updated{{color:var(--muted)}}.updated{{text-align:right;font-size:13px}}.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}.card{{background:linear-gradient(145deg,#151c29,#0f141e);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 12px 36px #0003}}.ticker{{font-weight:800;font-size:19px;letter-spacing:.04em}.dot{{display:inline-block;width:7px;height:7px;border-radius:50%;background:currentColor;margin-left:8px;vertical-align:middle}}.up .dot{{color:var(--green)}}.down .dot{{color:var(--red)}}.name{{color:var(--muted);font-size:12px;margin:8px 0 26px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.price{{font-size:25px;font-weight:750;letter-spacing:-.04em}}.change{{margin-top:8px;font-size:13px;font-weight:700}}.up .change{{color:var(--green)}}.down .change{{color:var(--red)}}section{{margin-top:42px;background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:8px 20px 20px}}.section-title{{padding:18px 0;color:var(--muted);font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:800}}table{{width:100%;border-collapse:collapse}}th,td{{padding:16px 8px;border-top:1px solid var(--line);text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{color:var(--muted);font-size:12px;font-weight:600}}td small{{display:block;color:var(--muted);font-size:11px;margin-top:4px}}td.up{{color:var(--green)}}td.down{{color:var(--red)}}.warning{{color:var(--warn);font-size:12px}}footer{{color:var(--muted);font-size:12px;margin-top:22px}}@media(max-width:800px){{.grid{{grid-template-columns:repeat(2,1fr)}}header{{display:block}}.updated{{text-align:left;margin-top:24px}}}}@media(max-width:460px){{main{{padding:28px 14px 48px}}.grid{{grid-template-columns:1fr}}section{{padding:4px 12px 12px;overflow:auto}}table{{min-width:520px}}}}</style></head><body><main><header><div><div class="eyebrow">Daily market intelligence</div><h1>Market<br>Recap.</h1><div class="sub">Five names. One clean read on the close.</div></div><div class="updated">Last updated<br><strong>{now}</strong></div></header><div class="grid">{"".join(cards)}</div><section><div class="section-title">Closing tape</div>{warning}<table><thead><tr><th>Asset</th><th>Close</th><th>Day change</th><th>Day %</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section><footer>Prices are end-of-day market data and may be delayed. Not investment advice.</footer></main></body></html>'''
    output_dir = Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
