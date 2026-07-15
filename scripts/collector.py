#!/usr/bin/env python3
"""Haul Analytics data collector. Pulls US trucking data and writes JSON files."""
import json, os, urllib.request
from datetime import datetime

DATA = os.path.expanduser('~/haul-analytics/data')
OUT_MARKET = os.path.join(DATA, 'market.json')
OUT_NEWS = os.path.join(DATA, 'news.json')
OUT_INCIDENTS = os.path.join(DATA, 'incidents.json')

def fetch_bls(series_ids):
    """Fetch US economic indicators from BLS public API."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": "2026",
        "endyear": "2026",
        "registrationkey": ""  # Free tier, no key needed
    }).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    
    if result['status'] != 'REQUEST_SUCCEEDED':
        raise Exception(f"BLS failed: {result.get('message')}")
    
    out = {}
    for s in result['Results']['series']:
        sid = s['seriesID']
        latest = s['data'][0] if s['data'] else None
        if latest:
            out[sid] = {
                'value': float(latest['value']),
                'period': f"{latest['periodName']} {latest['year']}"
            }
    return out

def collect_market():
    """Build market pulse indicators from BLS data."""
    bls = fetch_bls([
        'LNS14000000',  # Unemployment rate
        'CES0500000003',  # Avg hourly earnings (total private)
        'WPU057303',     # Diesel fuel PPI
        'CUUR0000SA0',   # CPI All items
    ])
    
    indicators = []
    
    # Unemployment
    if 'LNS14000000' in bls:
        v = bls['LNS14000000']['value']
        indicators.append({
            'label': 'Unemployment',
            'value': f'{v}%',
            'detail': f'US unemployment — {bls["LNS14000000"]["period"]}',
            'direction': 'down' if v < 4.5 else 'up',
            'what_it_means': 'Tight labor market means higher driver wages and recruiting costs for fleets.' if v < 4.5 else 'More available workers could ease driver shortage pressure.',
            'source': 'Bureau of Labor Statistics'
        })
    
    # Average Hourly Earnings
    if 'CES0500000003' in bls:
        v = bls['CES0500000003']['value']
        indicators.append({
            'label': 'Avg Hourly Earnings',
            'value': f'${v:.2f}',
            'detail': f'Private sector — {bls["CES0500000003"]["period"]}',
            'direction': 'up',
            'what_it_means': 'Rising wages pressure fleet operating margins. Driver pay is the largest cost after fuel.',
            'source': 'Bureau of Labor Statistics'
        })
    
    # Diesel PPI
    if 'WPU057303' in bls:
        v = bls['WPU057303']['value']
        prev_month = v - 2  # estimate
        direction = 'down' if v < 350 else 'up'
        indicators.append({
            'label': 'Diesel PPI',
            'value': f'{v:.1f}',
            'detail': f'Producer Price Index — {bls["WPU057303"]["period"]}',
            'direction': direction,
            'what_it_means': 'Wholesale diesel prices trending. Downstream pump prices typically follow within 2-4 weeks.',
            'source': 'Bureau of Labor Statistics'
        })
    
    # CPI
    if 'CUUR0000SA0' in bls:
        v = bls['CUUR0000SA0']['value']
        indicators.append({
            'label': 'Consumer Prices (CPI)',
            'value': f'{v:.1f}',
            'detail': f'All items index — {bls["CUUR0000SA0"]["period"]}',
            'direction': 'up' if v > 300 else 'down',
            'what_it_means': 'General inflation trends affect equipment costs, insurance, and operating expenses.',
            'source': 'Bureau of Labor Statistics'
        })
    
    return {
        'indicators': indicators,
        'updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    }

def collect_news():
    """Placeholder for US trucking news RSS feeds."""
    return {
        'headlines': [],
        'updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    }

def collect_incidents():
    """Placeholder for US road incidents from DOT/state 511 APIs."""
    return []

if __name__ == '__main__':
    print("Collecting Haul Analytics data...")
    
    # Market data (BLS)
    try:
        market = collect_market()
        with open(OUT_MARKET, 'w') as f:
            json.dump(market, f, indent=2)
        print(f"  Market: {len(market['indicators'])} indicators")
    except Exception as e:
        print(f"  Market error: {e}")
    
    # News (placeholder)
    with open(OUT_NEWS, 'w') as f:
        json.dump(collect_news(), f, indent=2)
    print("  News: placeholder")
    
    # Incidents (placeholder)
    with open(OUT_INCIDENTS, 'w') as f:
        json.dump(collect_incidents(), f, indent=2)
    print("  Incidents: placeholder")
    
    print("Done.")
