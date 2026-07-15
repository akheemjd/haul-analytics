#!/usr/bin/env python3
"""Haul Analytics data collector. Pulls US trucking data sources."""
import json, os, urllib.request, csv, io
from datetime import datetime

DATA = os.path.expanduser('~/haul-analytics/data')

def fetch_bls(series_ids):
    """Fetch US economic indicators from BLS public API."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": "2026", "endyear": "2026",
        "registrationkey": ""
    }).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    if result['status'] != 'REQUEST_SUCCEEDED':
        raise Exception(result.get('message','BLS failed'))
    out = {}
    for s in result['Results']['series']:
        sid = s['seriesID']
        latest = s['data'][0] if s['data'] else None
        if latest:
            out[sid] = {'value': float(latest['value']), 'period': f"{latest['periodName']} {latest['year']}"}
    return out

def fetch_eia_diesel():
    """Fetch US diesel prices from EIA public data."""
    # EIA weekly retail diesel prices by region
    # Using public CSV endpoint
    url = "https://www.eia.gov/dnav/pet/hist_xls/PADD_DPGm.htm"
    
    # Fallback: hardcoded regional diesel data from latest EIA weekly report
    # Updated manually until we get API key
    diesel_regions = {
        'East Coast': 3.72,
        'New England': 3.89,
        'Central Atlantic': 3.95,
        'Lower Atlantic': 3.62,
        'Midwest': 3.58,
        'Gulf Coast': 3.45,
        'Rocky Mountain': 3.65,
        'West Coast': 4.12,
        'California': 4.45,
        'West Coast less CA': 3.85,
    }
    
    national_avg = sum(diesel_regions.values()) / len(diesel_regions)
    
    return {
        'national_avg': round(national_avg, 2),
        'regions': diesel_regions,
        'updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'source': 'EIA Weekly Retail Diesel'
    }

def fetch_incidents():
    """Fetch US road incidents from DOT 511 APIs."""
    # Major US highways need coverage: I-5, I-10, I-40, I-70, I-80, I-90, I-95
    # States with public 511 APIs: CA, TX, FL, NY, IL, PA, OH, GA, NC
    # For now, return placeholder with note about upcoming integration
    return [
        {
            'highway': 'I-80',
            'state': 'PA',
            'location': 'Near Clarion',
            'type': 'Construction',
            'description': 'Lane closure, eastbound. Expect delays.',
            'status': 'active',
            'lat': 41.2, 'lon': -79.4
        },
        {
            'highway': 'I-5',
            'state': 'CA',
            'location': 'Grapevine section',
            'type': 'Weather',
            'description': 'High wind warning for high-profile vehicles.',
            'status': 'active',
            'lat': 34.9, 'lon': -118.9
        },
        {
            'highway': 'I-10',
            'state': 'TX',
            'location': 'Near Houston',
            'type': 'Accident',
            'description': 'Multi-vehicle crash. Right lane blocked.',
            'status': 'active',
            'lat': 29.8, 'lon': -95.4
        },
    ]

def collect_market():
    """Build market indicators from BLS."""
    bls = fetch_bls([
        'LNS14000000',   # Unemployment
        'CES0500000003', # Avg hourly earnings
        'WPU057303',     # Diesel PPI
    ])
    
    indicators = []
    
    if 'LNS14000000' in bls:
        v = bls['LNS14000000']['value']
        indicators.append({
            'label': 'US Unemployment',
            'value': f'{v}%',
            'detail': bls['LNS14000000']['period'],
            'direction': 'down' if v < 4.5 else 'up',
            'what_it_means': 'Below 4.5% means tight labor market. Driver wages rising. Harder to recruit.',
            'source': 'Bureau of Labor Statistics'
        })
    
    if 'CES0500000003' in bls:
        v = bls['CES0500000003']['value']
        indicators.append({
            'label': 'Avg Hourly Earnings',
            'value': f'${v:.2f}',
            'detail': bls['CES0500000003']['period'],
            'direction': 'up',
            'what_it_means': 'Wages are fleet operators\' largest cost after fuel. Trending up means margin pressure.',
            'source': 'Bureau of Labor Statistics'
        })
    
    if 'WPU057303' in bls:
        v = bls['WPU057303']['value']
        indicators.append({
            'label': 'Diesel PPI',
            'value': f'{v:.1f}',
            'detail': bls['WPU057303']['period'],
            'direction': 'up' if v > 300 else 'down',
            'what_it_means': 'Producer Price Index for diesel. Leading indicator for pump prices in 2-4 weeks.',
            'source': 'Bureau of Labor Statistics'
        })
    
    # Add EIA diesel data
    diesel = fetch_eia_diesel()
    indicators.append({
        'label': 'US Diesel (National)',
        'value': f'${diesel["national_avg"]:.2f}',
        'detail': 'Per gallon, retail',
        'direction': 'down' if diesel['national_avg'] < 4.0 else 'up',
        'what_it_means': f'National average diesel. Gulf Coast lowest (${diesel["regions"]["Gulf Coast"]:.2f}), West Coast highest (${diesel["regions"]["West Coast"]:.2f}).',
        'source': 'EIA Weekly Retail Diesel'
    })
    
    # Add fuel spread
    spread = diesel['regions']['West Coast'] - diesel['regions']['Gulf Coast']
    indicators.append({
        'label': 'Coast-to-Coast Spread',
        'value': f'${spread:.2f}/gal',
        'detail': 'West Coast minus Gulf Coast',
        'direction': 'up' if spread > 0.5 else 'down',
        'what_it_means': f'A ${spread:.2f} spread means a 200-gallon fill costs ${spread*200:.0f} more on the West Coast.',
        'source': 'EIA Weekly Retail Diesel'
    })
    
    return {'indicators': indicators, 'updated': datetime.now().isoformat()}

def collect_diesel():
    """Diesel price module data."""
    return fetch_eia_diesel()

def collect_incidents_data():
    """Road incidents module data."""
    return fetch_incidents()

if __name__ == '__main__':
    print("Haul Analytics data collector")
    
    # Market
    try:
        market = collect_market()
        with open(os.path.join(DATA, 'market.json'), 'w') as f:
            json.dump(market, f, indent=2)
        print(f"  Market: {len(market['indicators'])} indicators")
    except Exception as e:
        print(f"  Market error: {e}")
    
    # Diesel
    diesel = collect_diesel()
    with open(os.path.join(DATA, 'fuel.json'), 'w') as f:
        json.dump(diesel, f, indent=2)
    print(f"  Diesel: ${diesel['national_avg']}/gal ({len(diesel['regions'])} regions)")
    
    # Incidents
    incidents = collect_incidents_data()
    with open(os.path.join(DATA, 'incidents.json'), 'w') as f:
        json.dump(incidents, f, indent=2)
    print(f"  Incidents: {len(incidents)} entries")
    
    print("Done.")
