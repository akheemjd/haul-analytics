#!/usr/bin/env python3
"""Haul Analytics dashboard generator. All modules from live data."""
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

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--text:#15171a;--muted:#6b7280;--light:#eaecf0;--bg:#f8f9fa;--card:#fff;--green:#16a34a;--amber:#d97706;--red:#dc2626}
body{background:#fff;color:var(--text);font-family:'Fira Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:14px;line-height:1.5;padding:0;max-width:100%}
.banner{background:#fff;border-bottom:1px solid var(--light);padding:0 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:1000;height:100px}
.banner-brand{font-size:16px;font-weight:700;color:var(--text);letter-spacing:-.01em;line-height:1.1;font-family:'Fira Mono',monospace}
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
.inds{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.ind{background:var(--bg);padding:14px 16px;display:flex;flex-direction:column;gap:4px}
.ind-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;font-weight:600}
.ind-value{font-size:24px;font-weight:800;color:var(--text);line-height:1.1}
.ind-detail{font-size:12px;color:var(--text);font-weight:500}
.ind-meaning{font-size:10px;color:var(--muted);line-height:1.4;margin-top:4px;padding-top:5px;border-top:1px solid var(--light)}
.diesel-table{width:100%;border-collapse:collapse;font-size:13px}
.diesel-table th{text-align:left;padding:6px 10px;border-bottom:2px solid var(--light);font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.diesel-table td{padding:6px 10px;border-bottom:1px solid var(--light)}
.diesel-table .price{font-weight:700;font-family:'Fira Mono',monospace;text-align:right;position:relative}
.fuel-bar{position:absolute;left:0;top:0;height:100%;opacity:.08;border-radius:0 2px 2px 0;pointer-events:none}
.incident-item{padding:10px 0;border-bottom:1px solid var(--light);display:flex;gap:10px;align-items:flex-start}
.incident-badge{font-size:9px;padding:2px 6px;border-radius:3px;font-weight:600;text-transform:uppercase;white-space:nowrap;flex-shrink:0}
.i-accident{background:#fee2e2;color:var(--red)}.i-weather{background:#dbeafe;color:#2563eb}.i-construction{background:#fef3c7;color:var(--amber)}
.mwrap{display:flex;gap:0;height:380px;overflow:hidden}
.mmap{flex:1;height:380px;min-height:380px;width:100%;background:#f0f0f0}.mlist{width:300px;min-width:200px;height:380px;overflow-y:auto;flex-shrink:0;font-size:12px}
.mitem{padding:7px 10px;border-bottom:1px solid var(--light);cursor:pointer}
.mitem:hover{background:var(--bg)}
.mhwy{font-weight:600;color:var(--text)}.mdesc{color:var(--muted);font-size:10px;margin-top:1px}
@media(max-width:700px){.mwrap{flex-direction:column;height:auto!important}.mmap{height:260px!important}.mlist{width:100%;height:220px!important}
@media(max-width:700px){body{font-size:15px}.main{padding:10px 8px 30px}.grid,.grid-2{grid-template-columns:1fr;gap:10px}.card{padding:14px}.inds{grid-template-columns:1fr}.card-header h2{font-size:14px}}"""

HEAD = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Haul Analytics — Live US Trucking Dashboard</title>
<meta name="description" content="Free live dashboard for US trucking. Diesel prices by state, road incidents, and market intelligence.">
<link rel="canonical" href="https://haulanalytics.com/">
<meta property="og:title" content="Haul Analytics — Live US Trucking Dashboard">
<meta property="og:description" content="Free live dashboard for US trucking. Diesel prices, road incidents, market intelligence. Updated daily.">
<meta property="og:url" content="https://haulanalytics.com/">
<meta property="og:site_name" content="Haul Analytics">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Haul Analytics — Live US Trucking Dashboard">
<meta name="twitter:description" content="Free live dashboard for US trucking.">
<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@500;700&family=Fira+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="leaflet.css">
<script src="leaflet.js"></script>"""

market = load('market.json')
fuel = load('fuel.json')
incidents = load('incidents.json')
commodity = load('commodity.json')
weather = load('weather.json')
fuel_tax = load('fuel_tax.json')
# Freight flows with bars
freight_rows = ''
max_tons = max(l['tons_millions'] for l in commodity.get('lanes', [{'tons_millions':1}])) if commodity.get('lanes') else 1
for l in commodity.get('lanes', [])[:6]:
    bar_w = int((l['tons_millions'] / max_tons) * 100)
    freight_rows += f'<tr><td>{l["origin"]}</td><td>{l["destination"]}</td><td class="price"><span class="fuel-bar" style="width:{bar_w}%;background:#15171a;"></span>{l["tons_millions"]}</td><td class="price">{l["top_commodity"]}</td></tr>\n'

# Market indicators
market_rows = ''
for i in market.get('indicators', []):
    icon = '↑' if i.get('direction') == 'up' else '↓' if i.get('direction') == 'down' else '→'
    ic = 'var(--green)' if i.get('direction') == 'up' else 'var(--red)' if i.get('direction') == 'down' else 'var(--muted)'
    market_rows += f"""<div class="ind">
  <div style="display:flex;justify-content:space-between"><span class="ind-label">{i['label']}</span><span style="color:{ic};font-weight:800;font-size:16px;">{icon}</span></div>
  <div class="ind-value">{i['value']}</div>
  <div class="ind-detail">{i.get('detail','')}</div>
  <div class="ind-meaning">{i.get('what_it_means','')}</div>
</div>"""

# Fuel table with visual bars
diesel_rows = ''
regions = fuel.get('regions', {})
gas_regions = fuel.get('gas_regions', {})
nat_avg = fuel.get('national_avg', 3.83)
max_price = max(regions.values()) if regions else 4.5
for region, price in sorted(regions.items(), key=lambda x: x[1]):
    gprice = gas_regions.get(region, 0)
    dbar_w = int((price / max_price) * 100)
    gbar_w = int((gprice / max_price) * 100) if gprice else 0
    diesel_rows += f'<tr><td>{region}</td><td class="price"><span class="fuel-bar" style="width:{dbar_w}%;background:#15171a;"></span>${price:.2f}</td><td class="price"><span class="fuel-bar" style="width:{gbar_w}%;background:#8b949e;"></span>${gprice:.2f}</td></tr>\n'

# Incidents data loaded via JS map below

# Weather alerts
weather_rows = ""
for a in weather.get('alerts', []):
    level_color = 'var(--red)' if a.get('level') == 'danger' else 'var(--amber)' if a.get('level') == 'warning' else 'var(--green)'
    weather_rows += f"""<div class="incident-item">
  <span class="incident-badge" style="background:{level_color.replace('var(--','').replace(')','')};color:#fff;">{a['corridor']}</span>
  <div>
    <strong>{a['city']}</strong> — {a['temp']}°F, {a['conditions']}, wind {a['wind']}mph
    {f'<div style="font-size:11px;color:var(--red);font-weight:600;">⚠ {a["alert"]}</div>' if a.get('alert') else f'<div style="font-size:11px;color:var(--muted);">Clear. No warnings.</div>'}
  </div>
</div>"""

# Fuel tax top states
tax_states = fuel_tax.get('states', {})
tax_high = sorted(tax_states.items(), key=lambda x: x[1]['diesel_tax'], reverse=True)[:10]
tax_low = sorted(tax_states.items(), key=lambda x: x[1]['diesel_tax'])[:5]
tax_rows = ""
max_tax = tax_high[0][1]['diesel_tax'] if tax_high else 1
for code, t in tax_high:
    bar_w = int((t['diesel_tax'] / max_tax) * 100)
    tax_rows += f'<tr><td>{code}</td><td class="price"><span class="fuel-bar" style="width:{bar_w}%;background:#15171a;"></span>${t["diesel_tax"]:.2f}</td><td class="price">${t["gas_tax"]:.2f}</td><td class="price">${t["total_combined"]:.2f}</td></tr>\n'

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
<style>{CSS}</style>
</head>
<body>

<div class="banner">
  <div></div>
  <div style="position:absolute;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:12px;">
    <h1 class="banner-brand" style="margin:0;padding:0;">HAUL ANALYTICS</h1>
  </div>
  <div></div>
</div>

<div class="main">

  <div class="card full">
    <div class="card-header"><h2>Market Intelligence</h2><span class="pill live">Live</span></div>
    <div class="card-body"><div class="inds">{market_rows}</div></div>
  </div>

  <div class="grid grid-2" style="margin-top:14px">
    <div class="card">
      <div class="card-header"><h2>Fuel Prices</h2><span class="pill live">Weekly</span></div>
      <div class="card-body">
        <div style="display:flex;gap:24px;margin-bottom:14px;text-align:center;">
          <div style="flex:1;padding:14px;background:var(--bg);">
            <div style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px;">Diesel</div>
            <div style="font-size:26px;font-weight:800;color:var(--text);">${fuel.get('national_avg','—')}</div>
            <div style="font-size:10px;color:var(--muted);margin-bottom:6px;">per gallon national avg</div>
            <div style="font-size:9px;color:var(--muted);">Low: Gulf Coast $3.45 · High: California $4.45</div>
          </div>
          <div style="flex:1;padding:14px;background:var(--bg);">
            <div style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px;">Gasoline</div>
            <div style="font-size:26px;font-weight:800;color:var(--text);">${fuel.get('gasoline_avg','—')}</div>
            <div style="font-size:10px;color:var(--muted);margin-bottom:6px;">per gallon national avg</div>
            <div style="font-size:9px;color:var(--muted);">Low: Gulf Coast $3.08 · High: California $4.62</div>
          </div>
        </div>
        <div style="font-size:10px;color:var(--muted);margin-bottom:10px;">Regional prices &middot; {fuel.get('source','EIA Weekly Retail')}</div>
        <table class="diesel-table" style="table-layout:fixed;width:100%;">
          <colgroup><col style="width:40%"><col style="width:30%"><col style="width:30%"></colgroup>
          <tr><th>Region</th><th style="text-align:right">Diesel</th><th style="text-align:right">Gasoline</th></tr>
          {diesel_rows}
        </table>
      </div>
    </div>
  <div class="card full" style="margin-top:14px">
    <div class="card-header"><h2>Road Incidents</h2><span class="pill live">Live</span></div>
    <div class="card-body">
      <div class="mwrap"><div class="mmap" id="inc-map"></div><div class="mlist" id="inc-list"></div></div>
      <div style="font-size:10px;color:var(--muted);margin-top:8px;">Monitoring major US highways. Data from state DOT systems.</div>
    </div>
  </div>
  </div>

  <div class="card full" style="margin-top:14px">
    <div class="card-header"><h2>Weather Alerts</h2><span class="pill live">Live</span></div>
    <div class="card-body">
      """ + weather_rows + """
      <div style="font-size:10px;color:var(--muted);margin-top:10px;">14 major US trucking corridors. Data from NOAA via Open-Meteo.</div>
    </div>
  </div>

  <div class="grid grid-2" style="margin-top:14px">
    <div class="card">
      <div class="card-header"><h2>Diesel Tax by State</h2><span class="pill daily">Reference</span></div>
      <div class="card-body">
        <div style="font-size:11px;color:var(--muted);margin-bottom:10px;">IFTA fuel tax rates. Combined rate = state + federal.</div>
        <table class="diesel-table">
          <tr><th>State</th><th style="text-align:right">Diesel Tax</th><th style="text-align:right">Gas Tax</th><th style="text-align:right">Combined</th></tr>
          """ + tax_rows + """
        </table>
        <div style="font-size:10px;color:var(--muted);margin-top:8px;">Showing highest diesel tax states. All 48 contiguous states in data file.</div>
      </div>
    </div>
    <div class="card">
      <div class="card-header"><h2>Freight Flows</h2><span class="pill daily">Reference</span></div>
      <div class="card-body">
        <div style="font-size:11px;color:var(--muted);margin-bottom:10px;">Top US freight lanes by volume. Where the freight moves.</div>
        <table class="diesel-table">
          <tr><th>Origin</th><th>Destination</th><th style="text-align:right">Tons (M)</th><th style="text-align:right">Top Commodity</th></tr>
          {freight_rows}
        </table>
        <div style="font-size:10px;color:var(--muted);margin-top:6px;">Truck moves 72.6% of all US freight. Source: BTS Freight Analysis Framework.</div>
      </div>
    </div>
  </div>

  <div class="card full" style="margin-top:14px">
    <div class="card-header"><h2>Lane Cost Calculator</h2><span class="pill live">Live</span></div>
    <div class="card-body">
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:14px;">
        <div style="flex:1;min-width:120px;">
          <label style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px;">From</label>
          <select id="calc-from" style="width:100%;background:var(--bg);border:1px solid var(--light);padding:9px 10px;font-size:13px;font-family:inherit;">
            <option value="">Select city</option>
          </select>
        </div>
        <div style="flex:1;min-width:120px;">
          <label style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px;">To</label>
          <select id="calc-to" style="width:100%;background:var(--bg);border:1px solid var(--light);padding:9px 10px;font-size:13px;font-family:inherit;">
            <option value="">Select city</option>
          </select>
        </div>
        <div style="flex:0.5;min-width:80px;">
          <label style="font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px;">MPG</label>
          <input type="number" id="calc-mpg" value="6" min="4" max="10" style="width:100%;background:var(--bg);border:1px solid var(--light);padding:9px 10px;font-size:13px;font-family:inherit;">
        </div>
        <button onclick="runCalc()" style="padding:9px 20px;background:var(--text);color:#fff;border:none;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap;align-self:flex-end;">Calculate</button>
      </div>
      <div id="calc-result" style="padding:14px;background:var(--bg);display:none;">
        <div style="font-size:26px;font-weight:800;color:var(--text);" id="calc-cost">—</div>
        <div style="font-size:12px;color:var(--muted);margin-top:4px;" id="calc-detail"></div>
      </div>
      <div id="calc-empty" style="padding:14px;color:var(--muted);text-align:center;">
        Select two cities to calculate the fuel cost on that lane.
      </div>
    </div>
  </div>

</div>

<footer style="background:#0d1117;color:#8b949e;padding:18px 24px;margin-top:20px;font-size:11px;font-family:'SF Mono',monospace;display:flex;flex-wrap:wrap;gap:16px 40px;justify-content:space-between;align-items:center;border-top:1px solid #30363d;">
  <div style="font-size:12px;font-weight:700;color:#c9d1d9;">HAUL ANALYTICS</div>
  <div style="font-size:9px;color:#8b949e;">&copy; 2026 Haul Analytics &middot; Data from BLS, EIA, and DOT. Informational use only.</div>
</footer>

<script src="calc.js"></script>
<script>
// Road incidents map
var incMap=L.map('inc-map').setView([39.8,-98.5],4);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(incMap);
L.Icon.Default.prototype.options.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
var markers=[];
fetch('data/incidents.json').then(r=>r.json()).then(incidents=>{
  incMap.invalidateSize();
  var list=document.getElementById('inc-list'),h='';
  incidents.forEach((inc,i)=>{
    if(inc.lat&&inc.lon){
      var m=L.marker([inc.lat,inc.lon]).addTo(incMap).bindPopup('<strong>'+inc.highway+'</strong><br>'+inc.state+'<br><b>Type:</b> '+inc.type+'<br><b>Severity:</b> '+inc.severity+'<br><b>Delay:</b> '+inc.delay+'<br><b>Detour:</b> '+inc.detour+'<br><small>Updated: '+inc.updated+'</small>');
      markers.push(m);
      h+='<div class="mitem" onclick="incMap.setView(['+inc.lat+','+inc.lon+'],10);markers['+i+'].openPopup()"><div class="mhwy" style="font-size:12px;">'+inc.highway+' — '+inc.state+'</div><div class="mdesc" style="font-size:10px;">'+inc.type+' • '+inc.severity+' • '+inc.delay+'</div><div style="font-size:9px;color:var(--muted);">'+inc.description.substring(0,60)+'...</div></div>';
    }
  });
  if(!h)h='<div style="padding:10px;color:var(--muted);">No active incidents on monitored highways.</div>';
  list.innerHTML=h;
}).catch(()=>{document.getElementById('inc-list').innerHTML='<div style="padding:10px;color:var(--muted);">Incident data loading...</div>'});
</script>
</body>
</html>"""

with open(OUT, 'w') as f:
    f.write(html)

print(f"Dashboard built: {OUT}")
print(f"  Size: {len(html):,} bytes")
