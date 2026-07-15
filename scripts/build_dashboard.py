#!/usr/bin/env python3
"""Haul Analytics dashboard generator."""
import json, os
from datetime import datetime

BASE = os.path.expanduser('~/haul-analytics')
OUT = os.path.join(BASE, 'docs/index.html')
DATA = os.path.join(BASE, 'data')

def load(name):
    path = os.path.join(DATA, name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def ft(ts):
    try: return datetime.fromisoformat(ts).strftime('%b %d, %I:%M %p ET')
    except: return ts

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--text:#15171a;--muted:#6b7280;--light:#eaecf0;--bg:#f8f9fa;--card:#fff;--green:#16a34a;--amber:#d97706;--red:#dc2626;--radius:0}
body{background:#fff;color:var(--text);font-family:'Fira Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:14px;line-height:1.5;padding:0;max-width:100%}
.banner{background:#fff;border-bottom:1px solid var(--light);padding:0 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:1000;height:100px}
.banner-brand{font-size:16px;font-weight:700;color:var(--text);letter-spacing:-.01em;line-height:1.1;font-family:'Fira Mono',monospace}
.banner-sub{font-size:11px;color:var(--muted);font-weight:400}
.main{padding:14px 18px 40px;max-width:1440px;margin:0 auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:14px}
.grid-2{grid-template-columns:repeat(2,1fr)}
.card{background:#fff;border:1px solid var(--light);padding:18px;scroll-margin-top:70px}
.card.full{grid-column:1/-1}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--light);gap:10px}
.card-header h2{font-size:15px;font-weight:700;color:var(--text);font-family:'Fira Mono',monospace}
.card-body{min-height:30px}
.pill{font-size:9px;padding:3px 8px;border-radius:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.pill.live{background:#dcfce7;color:var(--green);animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
.pill.daily{background:#f1f5f9;color:var(--text)}
.inds{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.ind{background:var(--bg);padding:16px 18px;display:flex;flex-direction:column;gap:5px}
.ind-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;font-weight:600}
.ind-value{font-size:26px;font-weight:800;color:var(--text);line-height:1.1}
.ind-detail{font-size:13px;color:var(--text);font-weight:500}
.ind-meaning{font-size:11px;color:var(--muted);line-height:1.4;margin-top:5px;padding-top:6px;border-top:1px solid var(--light)}
@media(max-width:700px){body{font-size:15px}.main{padding:10px 8px 30px}.grid,.grid-2{grid-template-columns:1fr;gap:10px}.card{padding:14px}.inds{grid-template-columns:1fr}.card-header h2{font-size:14px}}"""

HEAD = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Haul Analytics — Live US Trucking Dashboard</title>
<meta name="description" content="Free live dashboard for US trucking. Diesel prices by state, lane data, road incidents, and market intelligence.">
<link rel="canonical" href="https://haulanalytics.com/">
<meta property="og:title" content="Haul Analytics — Live US Trucking Dashboard">
<meta property="og:description" content="Free live dashboard for US trucking. Diesel prices, lane data, road incidents. Updated every 30 minutes.">
<meta property="og:url" content="https://haulanalytics.com/">
<meta property="og:site_name" content="Haul Analytics">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Haul Analytics — Live US Trucking Dashboard">
<meta name="twitter:description" content="Free live dashboard for US trucking. Diesel prices by state, lane data, road incidents.">
<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@500;700&family=Fira+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">"""

# Load data
market = load('market.json')

# Build market indicators HTML
market_html = '<div class="inds">'
for i in market.get('indicators', []):
    icon = '↑' if i.get('direction') == 'up' else '↓' if i.get('direction') == 'down' else '→'
    ic = 'var(--green)' if i.get('direction') == 'up' else 'var(--red)' if i.get('direction') == 'down' else 'var(--muted)'
    market_html += f"""<div class="ind">
  <div style="display:flex;justify-content:space-between"><span class="ind-label">{i['label']}</span><span style="color:{ic};font-weight:800;font-size:18px;">{icon}</span></div>
  <div class="ind-value">{i['value']}</div>
  <div class="ind-detail">{i.get('detail','')}</div>
  <div class="ind-meaning">{i.get('what_it_means','')}<br><span style="color:var(--muted);font-size:9px;">{i.get('source','')}</span></div>
</div>"""
market_html += '</div>'

update_time = ft(market.get('updated', '')) if market.get('updated') else datetime.now().strftime('%b %d, %I:%M %p ET')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
<style>{CSS}</style>
</head>
<body>

<div class="banner">
  <nav style="padding-left:250px;font-size:15px;font-weight:700;font-family:'Fira Mono',monospace;">
    <a href="https://haulanalytics.com" class="desk-link" style="color:var(--text);text-decoration:none;margin-right:18px;">Home</a>
    <a href="https://haulanalytics.com/about/" class="desk-link" style="color:var(--text);text-decoration:none;">About</a>
  </nav>
  <div style="position:absolute;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:12px;">
    <h1 class="banner-brand" style="margin:0;padding:0;">HAUL ANALYTICS</h1>
  </div>
  <div></div>
</div>

<div class="main">

  <div style="background:#f8f9fa;border:1px solid var(--light);padding:16px 20px;margin-bottom:14px;text-align:center;">
    <div style="font-size:13px;color:var(--muted);">Live US trucking dashboard — diesel prices by state, road incidents, lane data, and market intelligence. Updated: {update_time}</div>
  </div>

  <div class="card full">
    <div class="card-header"><h2>Market Intelligence</h2><span class="pill live">Live</span></div>
    <div class="card-body">{market_html}</div>
  </div>

  <div class="grid grid-2" style="margin-top:14px">
    <div class="card">
      <div class="card-header"><h2>Diesel Prices</h2><span class="pill daily">Coming Soon</span></div>
      <div class="card-body" style="color:var(--muted);padding:20px 0;">State-by-state diesel tracking coming soon. Data from EIA. <a href="https://www.eia.gov/petroleum/gasdiesel/" target="_blank" style="color:var(--text);">View current EIA data →</a></div>
    </div>
    <div class="card">
      <div class="card-header"><h2>Road Incidents</h2><span class="pill daily">Coming Soon</span></div>
      <div class="card-body" style="color:var(--muted);padding:20px 0;">Live road incidents and closures from US DOT and state 511 systems. Integration in progress.</div>
    </div>
  </div>

  <div class="card full" style="margin-top:14px">
    <div class="card-header"><h2>Lane Data</h2><span class="pill daily">Coming Soon</span></div>
    <div class="card-body" style="color:var(--muted);padding:20px 0;">Rate benchmarking and cost analysis for major US freight lanes. Sign up for updates when this launches.</div>
  </div>

</div>

<footer style="background:#0d1117;color:#8b949e;padding:18px 24px;margin-top:20px;font-size:11px;font-family:'SF Mono',monospace;line-height:1.5;display:flex;flex-wrap:wrap;gap:16px 40px;justify-content:space-between;align-items:center;border-top:1px solid #30363d;">
  <div style="font-size:12px;font-weight:700;color:#c9d1d9;letter-spacing:.02em;">HAUL ANALYTICS</div>
  <div style="font-size:9px;color:#8b949e;">&copy; 2026 Haul Analytics &middot; Data-driven intelligence for US trucking.</div>
</footer>

</body>
</html>"""

with open(OUT, 'w') as f:
    f.write(html)

print(f"Dashboard built: {OUT}")
print(f"  Size: {len(html):,} bytes")
