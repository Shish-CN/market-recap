#!/usr/bin/env python3
import html
from datetime import datetime, timezone
from pathlib import Path
import yfinance as yf

TICKERS = ["MU", "DRAM", "MRVL", "GDXU", "NBIS"]
NAMES = {"MU": "Micron Technology", "DRAM": "DRAM ETF", "MRVL": "Marvell Technology", "GDXU": "Gold Miners 2x", "NBIS": "Nebius Group"}

def fmt(value):
    return "—" if value is None else f"${value:,.2f}"

def main():
    cards = []
    rows = []
    for ticker in TICKERS:
        data = yf.download(ticker, period="2d", interval="1d", auto_adjust=False, progress=False)
        if data.empty or len(data) < 1:
            continue
        close = float(data["Close"].iloc[-1].iloc[0] if hasattr(data["Close"].iloc[-1], "iloc") else data["Close"].iloc[-1])
        previous = None
        if len(data) > 1:
            previous = float(data["Close"].iloc[-2].iloc[0] if hasattr(data["Close"].iloc[-2], "iloc") else data["Close"].iloc[-2])
        change = close - previous if previous is not None else None
        pct = change / previous * 100 if previous else None
        direction = "up" if (change or 0) >= 0 else "down"
        sign = "+" if (change or 0) >= 0 else ""
        cards.append(f'''<article class="card {direction}"><div class="ticker">{ticker}<span class="dot"></span></div><div class="name">{html.escape(NAMES[ticker])}</div><div class="price">{fmt(close)}</div><div class="change">{sign}{fmt(abs(change)).replace("$", "$")} <span>({sign}{pct:.2f}%)</span></div></article>''')
        rows.append(f"<tr><td><strong>{ticker}</strong><small>{html.escape(NAMES[ticker])}</small></td><td>{fmt(close)}</td><td class='{direction}'>{sign}{fmt(abs(change))}</td><td class='{direction}'>{sign}{pct:.2f}%</td></tr>")
    now = datetime.now(timezone.utc).strftime("%B %d, %Y · %H:%M UTC")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Market Recap</title><style>
:root{{--bg:#0a0d14;--panel:#111722;--line:#222b3c;--text:#f4f7fb;--muted:#8b96aa;--green:#45e0a2;--red:#ff6b82;--blue:#84a9ff}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 80% -10%,#1e2e55 0,transparent 35%),var(--bg);color:var(--text);font:15px Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}main{{max-width:1120px;margin:auto;padding:48px 24px 72px}}header{{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:42px}}h1{{font-size:clamp(2.4rem,6vw,5rem);line-height:.95;letter-spacing:-.07em;margin:8px 0 16px}}.eyebrow{{color:var(--blue);font-size:12px;font-weight:800;letter-spacing:.18em;text-transform:uppercase}}.sub,.updated{{color:var(--muted)}}.updated{{text-align:right;font-size:13px}}.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}.card{{background:linear-gradient(145deg,#151c29,#0f141e);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 12px 36px #0003}}.ticker{{font-weight:800;font-size:19px;letter-spacing:.04em}.dot{{display:inline-block;width:7px;height:7px;border-radius:50%;background:currentColor;margin-left:8px;vertical-align:middle}}.up .dot{{color:var(--green)}}.down .dot{{color:var(--red)}}.name{{color:var(--muted);font-size:12px;margin:8px 0 26px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.price{{font-size:25px;font-weight:750;letter-spacing:-.04em}}.change{{margin-top:8px;font-size:13px;font-weight:700}}.up .change,.up{{color:var(--green)}}.down .change,.down{{color:var(--red)}}.card.down{{color:var(--text)}}.card.up{{color:var(--text)}}section{{margin-top:42px;background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:8px 20px 20px}}.section-title{{padding:18px 0;color:var(--muted);font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:800}}table{{width:100%;border-collapse:collapse}}th,td{{padding:16px 8px;border-top:1px solid var(--line);text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{color:var(--muted);font-size:12px;font-weight:600}}td small{{display:block;color:var(--muted);font-size:11px;margin-top:4px}}td.up{{color:var(--green)}}td.down{{color:var(--red)}}footer{{color:var(--muted);font-size:12px;margin-top:22px}}@media(max-width:800px){{.grid{{grid-template-columns:repeat(2,1fr)}}header{{display:block}}.updated{{text-align:left;margin-top:24px}}}}@media(max-width:460px){{main{{padding:28px 14px 48px}}.grid{{grid-template-columns:1fr}}section{{padding:4px 12px 12px;overflow:auto}}table{{min-width:520px}}}}</style></head><body><main><header><div><div class="eyebrow">Daily market intelligence</div><h1>Market<br>Recap.</h1><div class="sub">Five names. One clean read on the close.</div></div><div class="updated">Last updated<br><strong>{now}</strong></div></header><div class="grid">{"".join(cards)}</div><section><div class="section-title">Closing tape</div><table><thead><tr><th>Asset</th><th>Close</th><th>Day change</th><th>Day %</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section><footer>Prices are end-of-day market data and may be delayed. Not investment advice.</footer></main></body></html>'''
    Path("docs").mkdir(exist_ok=True)
    Path("docs/index.html").write_text(page, encoding="utf-8")

if __name__ == "__main__":
    main()
