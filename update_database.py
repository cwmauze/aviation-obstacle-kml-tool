import os
import json
import zipfile
import io
import requests
from bs4 import BeautifulSoup

# --- CONSTANTS ---
DOF_URL = "https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dof/"
NASR_URL = "https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_latest_zip_url(base_url, keyword):
    """Scrapes the FAA page to find the most current ZIP file link."""
    response = requests.get(base_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if keyword.lower() in href.lower() and href.endswith('.zip'):
            # Handle relative vs absolute URLs
            if href.startswith('http'):
                return href
            return f"https://www.faa.gov{href}"
    raise Exception(f"Could not find a valid {keyword} ZIP link on {base_url}")

def parse_dms(dms_str, is_apt=False):
    dms_str = dms_str.strip()
    if not dms_str: return 0.0
    direction = dms_str[-1]
    
    if is_apt:
        parts = dms_str[:-1].split('-')
    else:
        parts = dms_str[:-1].split()
        
    if len(parts) != 3: return 0.0
    decimal = float(parts[0]) + (float(parts[1]) / 60.0) + (float(parts[2]) / 3600.0)
    if direction in ['S', 'W']: decimal = -decimal
    return decimal

def process_data():
    obstacles = []
    airports = {}
    metadata = {"dof_date": "Unknown", "apt_count": 0, "obs_count": 0}

    # --- 1. DOWNLOAD & PARSE DOF ---
    print("Fetching latest DOF ZIP...")
    dof_zip_url = get_latest_zip_url(DOF_URL, "dof")
    print(f"Downloading: {dof_zip_url}")
    
    r_dof = requests.get(dof_zip_url, headers=HEADERS)
    with zipfile.ZipFile(io.BytesIO(r_dof.content)) as z:
        # Find the .DAT file inside the zip (names change by cycle)
        dat_filename = next(name for name in z.namelist() if name.upper().endswith('.DAT'))
        with z.open(dat_filename) as f:
            for line_bytes in f:
                line = line_bytes.decode('utf-8', errors='ignore')
                
                if line.startswith("  CURRENCY DATE ="):
                    metadata["dof_date"] = line.split("=")[1].strip()
                    
                if len(line) < 100 or line.startswith("CUR") or line.startswith("-") or line.startswith("OAS") or line.startswith(" "):
                    continue
                try:
                    agl_str = line[83:88].strip()
                    if not agl_str.isdigit(): continue
                    
                    agl = int(agl_str)
                    if agl < 200: continue
                    
                    lat = parse_dms(line[35:47])
                    lon = parse_dms(line[48:61])
                    city = line[18:34].strip()
                    oas = line[0:9].strip()
                    
                    obstacles.append({"id": oas, "city": city, "lat": lat, "lon": lon, "agl": agl})
                except:
                    continue
                    
    metadata["obs_count"] = len(obstacles)
    print(f"Parsed {len(obstacles)} obstacles.")

    # --- 2. DOWNLOAD & PARSE NASR APT ---
    print("\nFetching latest NASR APT ZIP...")
    nasr_zip_url = get_latest_zip_url(NASR_URL, "28DaySubscription")
    print(f"Downloading: {nasr_zip_url}")
    
    r_nasr = requests.get(nasr_zip_url, headers=HEADERS)
    with zipfile.ZipFile(io.BytesIO(r_nasr.content)) as z:
        with z.open('APT.txt') as f:
            for line_bytes in f:
                line = line_bytes.decode('utf-8', errors='ignore')
                if line.startswith("APT"):
                    try:
                        loc_id = line[27:31].strip()
                        lat_str = line[526:540].strip()
                        lon_str = line[553:567].strip()
                        
                        lat = parse_dms(lat_str, is_apt=True)
                        lon = parse_dms(lon_str, is_apt=True)
                        
                        if loc_id:
                            airports[loc_id] = {"lat": lat, "lon": lon}
                    except:
                        continue
                        
    metadata["apt_count"] = len(airports)
    print(f"Parsed {len(airports)} airports/heliports.")

    # --- 3. SAVE JSON FILES ---
    with open("obstacles.json", 'w') as f:
        json.dump(obstacles, f, separators=(',', ':'))
    with open("airports.json", 'w') as f:
        json.dump(airports, f, separators=(',', ':'))
    with open("metadata.json", 'w') as f:
        json.dump(metadata, f)
        
    print("\nSuccess! Saved obstacles.json, airports.json, and metadata.json.")

if __name__ == "__main__":
    process_data()