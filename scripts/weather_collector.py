#!/usr/bin/env python3
"""Collect weather alerts for major US trucking corridors using Open-Meteo."""
import json, os, urllib.request
from datetime import datetime

DATA = os.path.expanduser('~/haul-analytics/data')

# Key trucking corridor checkpoints
CORRIDORS = {
    'I-5 PNW': {'lat': 45.52, 'lon': -122.68, 'name': 'Portland, OR'},
    'I-5 CA': {'lat': 34.05, 'lon': -118.24, 'name': 'Los Angeles, CA'},
    'I-10 TX': {'lat': 29.76, 'lon': -95.37, 'name': 'Houston, TX'},
    'I-10 AZ': {'lat': 33.45, 'lon': -112.07, 'name': 'Phoenix, AZ'},
    'I-40 NM': {'lat': 35.08, 'lon': -106.65, 'name': 'Albuquerque, NM'},
    'I-70 CO': {'lat': 39.74, 'lon': -104.99, 'name': 'Denver, CO'},
    'I-70 KS': {'lat': 39.10, 'lon': -94.58, 'name': 'Kansas City, MO'},
    'I-80 WY': {'lat': 41.14, 'lon': -104.82, 'name': 'Cheyenne, WY'},
    'I-80 IL': {'lat': 41.88, 'lon': -87.63, 'name': 'Chicago, IL'},
    'I-90 MT': {'lat': 45.78, 'lon': -108.51, 'name': 'Billings, MT'},
    'I-90 MN': {'lat': 44.98, 'lon': -93.27, 'name': 'Minneapolis, MN'},
    'I-95 NY': {'lat': 40.71, 'lon': -74.01, 'name': 'New York, NY'},
    'I-95 FL': {'lat': 25.76, 'lon': -80.19, 'name': 'Miami, FL'},
    'I-95 VA': {'lat': 37.54, 'lon': -77.43, 'name': 'Richmond, VA'},
}

def weather_code_desc(code):
    codes = {0: 'Clear', 1: 'Mostly clear', 2: 'Partly cloudy', 3: 'Overcast',
             45: 'Fog', 48: 'Freezing fog', 51: 'Light drizzle', 53: 'Drizzle',
             55: 'Heavy drizzle', 61: 'Light rain', 63: 'Rain', 65: 'Heavy rain',
             71: 'Light snow', 73: 'Snow', 75: 'Heavy snow', 77: 'Snow grains',
             80: 'Rain showers', 81: 'Moderate rain', 82: 'Heavy rain',
             85: 'Snow showers', 86: 'Heavy snow', 95: 'Thunderstorm',
             96: 'Thunderstorm w/ hail', 99: 'Thunderstorm w/ heavy hail'}
    return codes.get(code, f'Unknown ({code})')

def fetch_weather(lat, lon):
    url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
           f'&current=temperature_2m,wind_speed_10m,wind_gusts_10m,weather_code,relative_humidity_2m'
           f'&temperature_unit=fahrenheit&wind_speed_unit=mph&forecast_days=1')
    req = urllib.request.Request(url, headers={'User-Agent': 'HaulAnalytics/1.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())['current']

def collect_weather():
    alerts = []
    
    for corridor, loc in CORRIDORS.items():
        try:
            w = fetch_weather(loc['lat'], loc['lon'])
            desc = weather_code_desc(w['weather_code'])
            temp = w['temperature_2m']
            wind = w['wind_speed_10m']
            gusts = w['wind_gusts_10m']
            
            # Determine alert level
            alert = None
            if gusts > 40:
                alert = 'HIGH WIND — Gusts ' + str(round(gusts)) + ' mph. High-profile vehicle risk.'
            elif gusts > 30:
                alert = 'Windy — Gusts ' + str(round(gusts)) + ' mph. Caution for high-profile vehicles.'
            elif w['weather_code'] in [45, 48]:
                alert = 'FOG — Reduced visibility.'
            elif w['weather_code'] in [71, 73, 75, 77, 85, 86]:
                alert = 'SNOW — Slippery conditions.'
            elif w['weather_code'] in [95, 96, 99]:
                alert = 'THUNDERSTORM — Possible delays.'
            elif temp < 32 and w['weather_code'] in [61, 63, 65, 80, 81, 82]:
                alert = 'FREEZING RAIN — Ice risk.'
            
            level = 'danger' if gusts > 40 or w['weather_code'] in [75, 86, 96, 99] or (temp < 32 and w['weather_code'] in [63, 65]) else 'warning' if alert else 'normal'
            
            alerts.append({
                'corridor': corridor,
                'city': loc['name'],
                'temp': round(temp),
                'wind': round(wind),
                'gusts': round(gusts),
                'conditions': desc,
                'alert': alert,
                'level': level,
            })
        except Exception as e:
            alerts.append({
                'corridor': corridor,
                'city': loc['name'],
                'error': str(e)[:60],
                'level': 'unavailable'
            })
    
    return {
        'alerts': alerts,
        'updated': datetime.now().isoformat(),
        'source': 'Open-Meteo / NOAA'
    }

if __name__ == '__main__':
    data = collect_weather()
    path = os.path.join(DATA, 'weather.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
    dangerous = [a for a in data['alerts'] if a.get('alert')]
    print(f"Weather: {len(data['alerts'])} corridors, {len(dangerous)} alerts")
    for a in dangerous:
        print(f"  {a['corridor']}: {a['alert']}")
