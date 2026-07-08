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


## Pipe in real incidents

The next-phase backend proxy is in `server.py`:

```bash
INCIDENTS_ENDPOINT="https://your-real-incident-feed.example/api/incidents" INCIDENTS_TOKEN="optional-bearer-token" python3 server.py
```

Then open: http://localhost:8765

`index.html` now polls `/api/live-incidents` when served by `server.py`. The proxy accepts common feed shapes like `{ "incidents": [...] }`, `{ "alerts": [...] }`, `{ "data": [...] }`, or a raw array, and normalizes them into the dashboard schema.

Important: GitHub Pages cannot run `server.py`, so the public GitHub Pages demo keeps using static `data.json` until this is deployed to a host that can run a backend, like Render/Fly/Cloud Run/Railway/Vercel serverless.
