# Citizen CMS Live Dashboard Scaffold

This is the Citizen Design prototype wired for live-refresh data.

## Run locally

```bash
cd /Users/citizenclaw/.hermes/workspace/state/product-grill/cms-live-dashboard
python3 server.py
```

Open: http://localhost:8765

## How live data works

`index.html` polls `data.json` every 15 seconds. Replace `LIVE_ENDPOINT = './data.json'` with a real backend endpoint when ready.

Recommended production sources:
- incidents / confirmation state
- VI roster + on-duty location feed
- site-level response target stats
- hospital destination advisory feed
- audit log / permission service

Hard guardrails remain:
- human confirmation before dispatch
- site-local supervisor authority
- break-glass cross-site override only
- no public/community access
- AI draft fields require staff confirmation
