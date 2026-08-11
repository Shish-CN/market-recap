# Market Recap

A daily dark-themed market dashboard for MU, DRAM, MRVL, GDXU, and NBIS.

The scheduled GitHub Actions workflow runs after the US market close, downloads daily market data with `yfinance`, generates `docs/index.html`, and publishes `docs/` to GitHub Pages.

## First-time setup

1. Open Settings > Pages.
2. Under Build and deployment, choose GitHub Actions.
3. Run the `Daily market recap` workflow once from the Actions tab.
4. The site will be available at `https://shish-cn.github.io/market-recap/` after Pages finishes deploying.

The workflow can also be started manually with `workflow_dispatch`. Data is sourced from Yahoo Finance through yfinance; verify licensing and availability are appropriate for your use before relying on it.
