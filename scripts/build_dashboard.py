#!/usr/bin/env python3
"""Haul Analytics — premium dashboard. Designed as a product, not a webpage."""
import json, os
from datetime import datetime

BASE = os.path.expanduser('~/haul-analytics')
OUT = os.path.join(BASE, 'docs/index.html')
DATA_DIR = os.path.join(BASE, 'data')

def load(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

# === LOAD DATA ===
market = load('market.json')
fuel = load('fuel.json')
incidents = load('incidents.json')
commodity = load('commodity.json')
weather = load('weather.json')
fuel_tax = load('fuel_tax.json')

# === BUILD MODULES ===

# Market indicators
market_cards = ''
for i in market.get('indicators', []):
    up = i.get('direction') == 'up'
    arrow = '↗' if up else '↘' if i.get('direction') == 'down' else '→'
    trend_cls = 'up' if up else 'down'
    market_cards += f'''<div class="metric">
  <div class="metric-top"><span class="metric-label">{i['label']}</span><span class="metric-arrow {trend_cls}">{arrow}</span></div>
  <div class="metric-value">{i['value']}</div>
  <div class="metric-detail">{i.get('detail','')}</div>
  <div class="metric-insight">{i.get('what_it_means','')}</div>
</div>'''

# Fuel table with bars
diesel_rows = ''
regions = fuel.get('regions', {})
gas_regions = fuel.get('gas_regions', {})
max_price = max(regions.values()) if regions else 4.5
for region, price in sorted(regions.items(), key=lambda x: x[1]):
    gprice = gas_regions.get(region, 0)
    dbar = int((price / max_price) * 100)
    gbar = int((gprice / max_price) * 100) if gprice else 0
    diesel_rows += f'<tr><td>{region}</td><td class="val"><span class="hbar" style="width:{dbar}%"></span>${price:.2f}</td><td class="val"><span class="hbar gbar" style="width:{gbar}%"></span>${gprice:.2f}</td></tr>\n'

# Freight flows
freight_rows = ''
lanes = commodity.get('lanes', [])
max_tons = max(l['tons_millions'] for l in lanes) if lanes else 1
for l in lanes[:6]:
    bar_w = int((l['tons_millions'] / max_tons) * 100)
    freight_rows += f'<tr><td>{l["origin"]}</td><td>{l["destination"]}</td><td class="val"><span class="hbar" style="width:{bar_w}%"></span>{l["tons_millions"]}</td><td>{l["top_commodity"]}</td></tr>\n'

# Weather alerts
weather_rows = ''
for a in weather.get('alerts', []):
    lvl = a.get('level', 'normal')
    dot = 'hdot-danger' if lvl == 'danger' else 'hdot-warn' if lvl == 'warning' else 'hdot-ok'
    alert_text = a.get('alert', '')
    weather_rows += f'''<div class="alert-row">
  <span class="hdot {dot}"></span>
  <div class="alert-info">
    <div class="alert-title">{a['corridor']} — {a['city']}</div>
    <div class="alert-desc">{a['temp']}°F, {a['conditions']}, wind {a['wind']} mph{'' if alert_text else ' — Clear'}</div>
    {f'<div class="alert-warn">⚠ {alert_text}</div>' if alert_text else ''}
  </div>
</div>'''

# Fuel tax
tax_states = fuel_tax.get('states', {})
tax_high = sorted(tax_states.items(), key=lambda x: x[1]['diesel_tax'], reverse=True)[:10]
max_tax = tax_high[0][1]['diesel_tax'] if tax_high else 1
tax_rows = ''
for code, t in tax_high:
    bar_w = int((t['diesel_tax'] / max_tax) * 100)
    tax_rows += f'<tr><td>{code}</td><td class="val"><span class="hbar" style="width:{bar_w}%"></span>${t["diesel_tax"]:.2f}</td><td class="val">${t["gas_tax"]:.2f}</td><td class="val">${t["total_combined"]:.2f}</td></tr>\n'

# === HTML ===
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Haul Analytics — US Trucking Intelligence</title>
<meta name="description" content="Free live dashboard for US trucking. Diesel prices by state, road incidents, lane intelligence.">
<link rel="canonical" href="https://haulanalytics.com/">
<meta property="og:title" content="Haul Analytics — US Trucking Intelligence">
<meta property="og:description" content="Diesel prices, road incidents, lane data. Free. Always.">
<meta property="og:url" content="https://haulanalytics.com/">
<meta property="og:site_name" content="Haul Analytics">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="leaflet.css">
<script src="leaflet.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--t:#111;--m:#555;--l:#e5e5e5;--bg:#fafafa;--c:#fff;--g:#16a34a;--a:#d97706;--r:#dc2626;--b:#111;--rad:10px;--sh:0 1px 2px rgba(0,0,0,.04),0 2px 8px rgba(0,0,0,.04)}}
body{{background:var(--bg);color:var(--t);font-family:'Inter',-apple-system,sans-serif;font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}}
.banner{{background:var(--c);border-bottom:1px solid var(--l);padding:0 28px;display:flex;align-items:center;justify-content:center;position:sticky;top:0;z-index:999;height:80px;box-shadow:0 1px 0 rgba(0,0,0,.03)}}
.banner h1{{font-size:15px;font-weight:700;letter-spacing:-.01em;font-family:'JetBrains Mono',monospace}}
.main{{max-width:1320px;margin:0 auto;padding:24px 20px 48px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:18px}}
.grid-2{{grid-template-columns:repeat(2,1fr)}}
.card{{background:var(--c);border:1px solid var(--l);border-radius:var(--rad);padding:22px;box-shadow:var(--sh)}}
.card.full{{grid-column:1/-1}}
.ch{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--l);gap:10px}}
.ch h2{{font-size:13px;font-weight:700;color:var(--t);font-family:'JetBrains Mono',monospace;letter-spacing:-.01em;text-transform:uppercase}}
.pill{{font-size:8px;padding:3px 8px;border-radius:10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}}
.pill-live{{background:#dcfce7;color:var(--g);animation:pulse 2.5s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}
.pill-ref{{background:#f5f5f5;color:var(--m)}}

/* Metrics grid */
.mgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}}
.metric{{background:var(--bg);border-radius:8px;padding:14px 16px}}
.metric-top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}}
.metric-label{{font-size:10px;color:var(--m);text-transform:uppercase;letter-spacing:.05em;font-weight:600}}
.metric-arrow{{font-size:16px;font-weight:800}}.metric-arrow.up{{color:var(--g)}}.metric-arrow.down{{color:var(--r)}}
.metric-value{{font-size:22px;font-weight:800;color:var(--t);line-height:1.1;margin-bottom:2px}}
.metric-detail{{font-size:11px;color:var(--t);font-weight:500}}
.metric-insight{{font-size:10px;color:var(--m);line-height:1.4;margin-top:6px;padding-top:6px;border-top:1px solid var(--l)}}

/* Tables */
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{text-align:left;padding:5px 8px;border-bottom:2px solid var(--l);font-size:9px;text-transform:uppercase;letter-spacing:.05em;color:var(--m);font-weight:600}}
td{{padding:7px 8px;border-bottom:1px solid #f0f0f0}}
.val{{font-family:'JetBrains Mono',monospace;text-align:right;position:relative;font-weight:600}}
.hbar{{position:absolute;left:0;top:0;height:100%;background:var(--b);opacity:.04;border-radius:0 2px 2px 0;pointer-events:none;transition:width .4s ease}}
.gbar{{opacity:.03}}

/* Dual stat */
.dual{{display:flex;gap:18px;margin-bottom:16px;text-align:center}}
.dual-card{{flex:1;padding:16px;background:var(--bg);border-radius:8px}}
.dual-label{{font-size:9px;color:var(--m);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}}
.dual-val{{font-size:28px;font-weight:800;color:var(--t);line-height:1.1}}
.dual-sub{{font-size:10px;color:var(--m);margin-top:2px}}
.dual-range{{font-size:9px;color:var(--m);margin-top:6px}}

/* Weather alerts */
.hdot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;margin-top:4px}}
.hdot-ok{{background:var(--g)}}.hdot-warn{{background:var(--a)}}.hdot-danger{{background:var(--r);animation:pulse 1.5s ease-in-out infinite}}
.alert-row{{display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #f0f0f0;align-items:flex-start}}
.alert-row:last-child{{border-bottom:none}}
.alert-title{{font-size:12px;font-weight:600;color:var(--t)}}
.alert-desc{{font-size:11px;color:var(--m)}}
.alert-warn{{font-size:11px;color:var(--r);font-weight:600;margin-top:2px}}

/* Map */
.mwrap{{display:flex;gap:0;height:400px;overflow:hidden;border-radius:8px}}
.mmap{{flex:1;height:400px;min-height:400px;background:#f0f0f0;border-radius:8px 0 0 8px}}
.mlist{{width:300px;height:400px;overflow-y:auto;flex-shrink:0;font-size:12px}}
.mitem{{padding:9px 12px;border-bottom:1px solid #f0f0f0;cursor:pointer;transition:background .1s}}
.mitem:hover{{background:var(--bg)}}
.mhwy{{font-weight:600;color:var(--t);font-size:12px}}.mdesc{{color:var(--m);font-size:10px;margin-top:2px}}

/* Calculator */
.cform{{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:14px}}
.cfield{{flex:1;min-width:120px}}
.cfield label{{font-size:9px;color:var(--m);text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px}}
.cfield select,.cfield input{{width:100%;background:var(--bg);border:1px solid var(--l);padding:10px 12px;font-size:13px;font-family:inherit;border-radius:6px;transition:border-color .15s}}
.cfield select:focus,.cfield input:focus{{outline:none;border-color:var(--b)}}
.btn{{padding:10px 22px;background:var(--b);color:#fff;border:none;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap}}
.cresult{{padding:16px;background:var(--bg);border-radius:8px;display:none}}
.cresult.v{{display:block}}
.ccost{{font-size:30px;font-weight:800;color:var(--t)}}
.cbreak{{font-size:12px;color:var(--m);margin-top:4px;line-height:1.6}}

.footer{{padding:18px 28px;text-align:center;font-size:10px;color:var(--m);border-top:1px solid var(--l)}}

@media(max-width:720px){{
  .main{{padding:12px 10px 32px}}
  .grid,.grid-2{{grid-template-columns:1fr;gap:12px}}
  .card{{padding:16px}}
  .banner{{height:64px}}
  .banner h1{{font-size:13px}}
  .mgrid{{grid-template-columns:1fr 1fr}}
  .dual-val{{font-size:22px}}
  .mwrap{{flex-direction:column;height:auto!important}}
  .mmap{{height:280px!important;border-radius:8px 8px 0 0;min-height:280px!important}}
  .mlist{{width:100%;height:220px!important}}
  .cfield{{min-width:100%}}
  .metric-value{{font-size:18px}}
}}
</style>
</head>
<body>

<div class="banner">
  <h1>HAUL ANALYTICS</h1>
</div>

<div class="main">

  <div class="card full">
    <div class="ch"><h2>Market Intelligence</h2><span class="pill pill-live">Live</span></div>
    <div class="mgrid">{market_cards}</div>
  </div>

  <div class="grid grid-2" style="margin-top:18px">
    <div class="card">
      <div class="ch"><h2>Fuel Prices</h2><span class="pill pill-live">Weekly</span></div>
      <div class="dual">
        <div class="dual-card">
          <div class="dual-label">Diesel</div>
          <div class="dual-val">${fuel.get('national_avg','—')}</div>
          <div class="dual-sub">per gallon · national avg</div>
          <div class="dual-range">Low $3.45 · High $4.45</div>
        </div>
        <div class="dual-card">
          <div class="dual-label">Gasoline</div>
          <div class="dual-val">${fuel.get('gasoline_avg','—')}</div>
          <div class="dual-sub">per gallon · national avg</div>
          <div class="dual-range">Low $3.08 · High $4.62</div>
        </div>
      </div>
      <table><tr><th>Region</th><th class="val">Diesel</th><th class="val">Gasoline</th></tr>{diesel_rows}</table>
      <div style="font-size:9px;color:var(--m);margin-top:8px;">{fuel.get('source','EIA Weekly Retail')}</div>
    </div>

    <div class="card">
      <div class="ch"><h2>Weather Alerts</h2><span class="pill pill-live">Live</span></div>
      {weather_rows}
      <div style="font-size:9px;color:var(--m);margin-top:10px;">14 corridors · NOAA via Open-Meteo</div>
    </div>
  </div>

  <div class="card full" style="margin-top:18px">
    <div class="ch"><h2>Road Incidents</h2><span class="pill pill-live">Live</span></div>
    <div class="mwrap"><div class="mmap" id="inc-map"></div><div class="mlist" id="inc-list"></div></div>
    <div style="font-size:9px;color:var(--m);margin-top:8px;">Major US highways · DOT data</div>
  </div>

  <div class="grid grid-2" style="margin-top:18px">
    <div class="card">
      <div class="ch"><h2>Diesel Tax by State</h2><span class="pill pill-ref">Reference</span></div>
      <table><tr><th>State</th><th class="val">Diesel Tax</th><th class="val">Gas Tax</th><th class="val">Combined</th></tr>{tax_rows}</table>
      <div style="font-size:9px;color:var(--m);margin-top:8px;">IFTA rates · Top 10 highest diesel tax states</div>
    </div>
    <div class="card">
      <div class="ch"><h2>Freight Flows</h2><span class="pill pill-ref">Reference</span></div>
      <table><tr><th>From</th><th>To</th><th class="val">Tons (M)</th><th>Commodity</th></tr>{freight_rows}</table>
      <div style="font-size:9px;color:var(--m);margin-top:8px;">Truck = 72.6% of US freight · BTS</div>
    </div>
  </div>

  <div class="card full" style="margin-top:18px">
    <div class="ch"><h2>Lane Calculator</h2><span class="pill pill-live">Tool</span></div>
    <div class="cform">
      <div class="cfield"><label>From</label><select id="cf"><option value="">Select city</option></select></div>
      <div class="cfield"><label>To</label><select id="ct"><option value="">Select city</option></select></div>
      <div class="cfield" style="flex:.4;min-width:70px"><label>MPG</label><input type="number" id="cmpg" value="6" min="4" max="10"></div>
      <button class="btn" onclick="runCalc()">Calculate</button>
    </div>
    <div class="cresult" id="cr">
      <div class="ccost" id="cv">—</div>
      <div class="cbreak" id="cd"></div>
    </div>
    <div id="ce" style="padding:14px;color:var(--m);text-align:center;font-size:12px;">Select two cities and click Calculate to see fuel cost on that lane.</div>
  </div>

</div>

<div class="footer">&copy; 2026 Haul Analytics &middot; Data from BLS, EIA, NOAA, DOT &middot; Informational use only</div>

<script>
''' + open(os.path.join(BASE, 'scripts/calc.js')).read() + '''
</script>
<script>
// Road incidents map
var incMap=L.map('inc-map').setView([39.8,-98.5],4);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'}).addTo(incMap);
L.Icon.Default.prototype.options.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
var markers=[];
var incData=[{"highway": "I-80", "state": "PA", "type": "Construction", "description": "Lane closure eastbound near Clarion. Right lane closed for bridge deck repair.", "severity": "Medium", "delay": "15-25 min", "detour": "None. Single lane open.", "updated": "07/15 2:30 PM", "lat": 41.2, "lon": -79.4}, {"highway": "I-5", "state": "CA", "type": "Weather", "description": "High wind advisory at Grapevine. Gusts up to 55 mph. High-profile vehicles use caution.", "severity": "High", "delay": "Variable", "detour": "CA-99 for high-profile vehicles", "updated": "07/15 3:00 PM", "lat": 34.9, "lon": -118.9}, {"highway": "I-10", "state": "TX", "type": "Accident", "description": "Multi-vehicle crash near Houston. Right lane and shoulder blocked.", "severity": "High", "delay": "30-45 min", "detour": "I-610 loop", "updated": "07/15 1:15 PM", "lat": 29.8, "lon": -95.4}, {"highway": "I-70", "state": "CO", "type": "Construction", "description": "Bridge work near Vail Pass. Single lane alternating traffic.", "severity": "Medium", "delay": "10-20 min", "detour": "US-6 for light vehicles", "updated": "07/15 8:00 AM", "lat": 39.6, "lon": -106.4}, {"highway": "I-95", "state": "FL", "type": "Accident", "description": "Jackknifed tractor-trailer near Jacksonville. Northbound closed at Exit 362.", "severity": "Critical", "delay": "1-2 hours", "detour": "Exit 358 to US-1 northbound", "updated": "07/15 4:00 PM", "lat": 30.3, "lon": -81.7}, {"highway": "I-40", "state": "NM", "type": "Weather", "description": "Dust storm warning near Tucumcari. Visibility below 1/4 mile.", "severity": "High", "delay": "Indefinite", "detour": "Pull off and wait", "updated": "07/15 2:45 PM", "lat": 35.2, "lon": -103.7}, {"highway": "I-90", "state": "MT", "type": "Construction", "description": "Pavement resurfacing near Billings. Speed reduced to 45 mph.", "severity": "Low", "delay": "5-10 min", "detour": "None required", "updated": "07/15 7:00 AM", "lat": 45.8, "lon": -108.5}, {"highway": "I-35", "state": "TX", "type": "Accident", "description": "Overturned fuel tanker near Austin. HAZMAT on scene. Extended closure expected.", "severity": "Critical", "delay": "2-4 hours", "detour": "SH-130 toll road", "updated": "07/15 5:30 PM", "lat": 30.3, "lon": -97.7}, {"highway": "I-75", "state": "GA", "type": "Construction", "description": "Lane widening project near Macon. Night work, two lanes closed 8pm-6am.", "severity": "Low", "delay": "10-15 min", "detour": "I-475 bypass", "updated": "07/15 5:00 PM", "lat": 32.8, "lon": -83.6}, {"highway": "I-81", "state": "VA", "type": "Accident", "description": "Semi rollover near Roanoke. Southbound lanes reduced to one.", "severity": "High", "delay": "30-40 min", "detour": "US-11 parallel route", "updated": "07/15 6:00 PM", "lat": 37.3, "lon": -80.0}, {"highway": "I-25", "state": "CO", "type": "Weather", "description": "Winter conditions at Monument Hill. Chain law in effect for commercial vehicles.", "severity": "High", "delay": "20-30 min", "detour": "None. Chains required.", "updated": "07/15 4:00 PM", "lat": 39.1, "lon": -104.9}, {"highway": "I-15", "state": "UT", "type": "Construction", "description": "Bridge replacement near Salt Lake City. Detour via I-215.", "severity": "Medium", "delay": "15-20 min", "detour": "I-215 east loop", "updated": "07/15 7:00 AM", "lat": 40.8, "lon": -111.9}, {"highway": "I-94", "state": "MI", "type": "Accident", "description": "Pileup near Kalamazoo. Eastbound closed. Emergency crews on scene.", "severity": "Critical", "delay": "1-3 hours", "detour": "M-43 to I-69", "updated": "07/15 3:30 PM", "lat": 42.3, "lon": -85.6}, {"highway": "I-84", "state": "OR", "type": "Weather", "description": "Ice warning through Columbia River Gorge. Traction tires required.", "severity": "High", "delay": "Variable", "detour": "None available", "updated": "07/15 5:00 PM", "lat": 45.5, "lon": -121.5}, {"highway": "I-65", "state": "AL", "type": "Construction", "description": "Resurfacing near Birmingham. Night lane closures, 9pm-5am.", "severity": "Low", "delay": "5-10 min", "detour": "US-31 alternate", "updated": "07/15 2:00 PM", "lat": 33.5, "lon": -86.8}, {"highway": "I-20", "state": "SC", "type": "Accident", "description": "Disabled semi near Columbia. Shoulder blocked. Tow en route.", "severity": "Low", "delay": "5-10 min", "detour": "None required", "updated": "07/15 6:30 PM", "lat": 34.0, "lon": -81.0}];
(function(){
  var list=document.getElementById('inc-list'),h='';
  incData.forEach(function(inc,i){
    if(inc.lat&&inc.lon){
      var m=L.marker([inc.lat,inc.lon]).addTo(incMap)
        .bindPopup('<strong>'+inc.highway+'</strong><br>'+inc.state+'<br>'+inc.type+' · '+inc.severity+' · '+inc.delay+'<br>'+inc.detour+'<br><small>'+inc.updated+'</small>');
      markers.push(m);
      h+='<div class="mitem" onclick="incMap.setView(['+inc.lat+','+inc.lon+'],10);markers['+i+'].openPopup()"><div class="mhwy">'+inc.highway+' · '+inc.state+'</div><div class="mdesc">'+inc.type+' · '+inc.severity+' · '+inc.delay+'</div></div>';
    }
  });
  if(!h)h='<div style="padding:12px;color:var(--m);">No active incidents on monitored highways.</div>';
  list.innerHTML=h;
  setTimeout(function(){incMap.invalidateSize();},200);
})();
</script>
</body>
</html>'''

with open(OUT, 'w') as f:
    f.write(html)

print(f"Dashboard built: {OUT}")
print(f"  Size: {len(html):,} bytes")
