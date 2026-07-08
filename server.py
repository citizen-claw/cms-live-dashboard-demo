#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json
import os
import time

ROOT = Path(__file__).parent
INCIDENTS_ENDPOINT = os.environ.get('INCIDENTS_ENDPOINT', '').strip()
INCIDENTS_TOKEN = os.environ.get('INCIDENTS_TOKEN', '').strip()
PORT = int(os.environ.get('PORT', '8765'))


def _tone(status):
    s = (status or '').lower()
    if any(x in s for x in ['critical', 'shot', 'shooting', 'gun', 'weapon']):
        return 'red'
    if any(x in s for x in ['risk', 'dispute', 'assault', 'police']):
        return 'yellow'
    if any(x in s for x in ['resolved', 'closed']):
        return 'green'
    return 'blue'


def _incident_title(item):
    return (
        item.get('title') or item.get('headline') or item.get('name') or
        item.get('event_type') or item.get('type') or 'Citizen Incident'
    )


def _incident_description(item):
    parts = []
    for key in ['description', 'summary', 'address', 'location_name', 'neighborhood']:
        val = item.get(key)
        if val and str(val) not in parts:
            parts.append(str(val))
    return '. '.join(parts) or 'Live incident feed item. Staff confirmation required before action.'


def _incident_status(item):
    raw = item.get('status') or item.get('state') or item.get('severity') or item.get('event_type') or 'MONITORING'
    return str(raw).upper().replace('_', ' ')[:18]


def normalize_feed(payload):
    # Accept common shapes: {incidents:[...]}, {alerts:[...]}, raw list, or {data:[...]}
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get('incidents') or payload.get('alerts') or payload.get('data') or payload.get('results') or []
    else:
        items = []
    alerts = []
    for item in items[:8]:
        if not isinstance(item, dict):
            continue
        status = _incident_status(item)
        alerts.append({
            'title': _incident_title(item),
            'status': status,
            'tone': item.get('tone') or _tone(status + ' ' + _incident_title(item)),
            'time': item.get('time') or item.get('age') or item.get('createdAgo') or 'live',
            'description': _incident_description(item),
        })
    return {
        'mission': {'value': payload.get('mission', {}).get('value', 'Live') if isinstance(payload, dict) else 'Live', 'scope': 'Real incidents'},
        'lastUpdated': time.strftime('%H:%M:%S'),
        'sites': payload.get('sites', []) if isinstance(payload, dict) else [],
        'alerts': alerts,
        'source': 'real' if INCIDENTS_ENDPOINT else 'demo'
    }


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve static files from this folder regardless of cwd.
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path == '/':
            path = '/index.html'
        return str(ROOT / path.lstrip('/'))

    def do_GET(self):
        if self.path.split('?', 1)[0] == '/api/live-incidents':
            self.send_live_incidents()
            return
        return super().do_GET()

    def send_json(self, code, obj):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_live_incidents(self):
        if not INCIDENTS_ENDPOINT:
            # Fallback keeps demo functional until a real endpoint/token is supplied.
            self.send_json(200, json.loads((ROOT / 'data.json').read_text()))
            return
        headers = {'Accept': 'application/json'}
        if INCIDENTS_TOKEN:
            headers['Authorization'] = f'Bearer {INCIDENTS_TOKEN}'
        try:
            req = Request(INCIDENTS_ENDPOINT, headers=headers)
            with urlopen(req, timeout=8) as res:
                payload = json.loads(res.read().decode('utf-8'))
            self.send_json(200, normalize_feed(payload))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
            self.send_json(502, {'error': 'live incident fetch failed', 'detail': str(e), 'fallback': json.loads((ROOT / 'data.json').read_text())})


if __name__ == '__main__':
    print(f'Citizen CMS live dashboard: http://localhost:{PORT}')
    if INCIDENTS_ENDPOINT:
        print('Live incident proxy enabled from INCIDENTS_ENDPOINT')
    else:
        print('No INCIDENTS_ENDPOINT set; /api/live-incidents falls back to data.json')
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
