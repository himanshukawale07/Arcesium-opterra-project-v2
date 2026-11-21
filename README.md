# Financial Data Stack — Independent Portfolio Project

Interactive Streamlit case study for investment reference and transactional data management.

**Important:** Independently designed using the publicly described Opterra Financial Data Stack capabilities as inspiration. Not affiliated with, endorsed by, or a replica of Arcesium or Opterra. All data is synthetic. No proprietary code, live feeds, client data or production connections are used.

## Features
- Security and issuer master with ISIN/CUSIP/SEDOL and universes
- Reference datasets: securities, prices, positions and corporate actions
- Firm- and portfolio-level pricing priority demonstration with freshness checks
- Source registry and CSV schema preview
- API and Snowflake Data Share concepts (simulated only)
- Executable data-quality rules and exception queue
- Transactions and counterparty master
- Historical price and portfolio analytics
- Dynamic Document Studio concept with Markdown and CSV exports
- Data distribution, lineage and controlled exports
- Product configuration and governance documentation

## Run locally (Windows PowerShell)
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy
Connect this repository to Streamlit Community Cloud and set the main file to `app.py`. The app reads CSVs from `data/` and supports root-level fallback.

## Scope boundaries
This uses local synthetic CSV data and deterministic demonstration logic. It does not implement live market feeds, real vendor adaptors, a running API server, Snowflake connectivity, production MDM, official valuations, regulatory reporting, enterprise security or production-scale throughput. Pricing rules are illustrative, not valuation advice.

See `docs/` for PRD, feature mapping, user stories, architecture, data dictionary, UAT and roadmap.
