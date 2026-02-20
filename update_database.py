import os
import json
import zipfile
import io
import requests
import datetime
import re
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DOF_URL = "https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dof/"

# Exact FAA APT.txt Column Slices (0-indexed)
APT_COLS = {
    'id': (27, 31),
    'name': (133, 183),
    'lat': (523, 538), 
    'lon': (550, 565)  
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_current_airac_cycle():
    base_date = datetime.date(2026, 1, 22) 
    today = datetime.date.today()
    delta = (today - base_date).days
    cycles_passed = delta // 28
    return base_date + datetime.timedelta(days=cycles_passed*28)

def get_dof_zip_url():
    response = requests.get(DOF_URL, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        if 'dof' in link['href'].lower() and link['href'].lower().endswith('.zip'):
            return link['href'] if link['href'].startswith('http') else f"https://www.faa.gov{link['href']}"
            
    match = re.search(r'["\']([^"\']*dof[^"\']*\.zip)["\']', response.text, re.IGNORECASE)
    if match:
        url = match.group(1)
        return url if url.startswith('http') else f"https://www.faa.gov{url}"
        
    raise Exception("Could not find a valid DOF ZIP link.")

def faa_to_decimal(s):
    if not s or s.strip() == "": return 0.0
    s = s.strip().upper()
    mult = -1 if ('S' in s or 'W' in s) else 1
    clean = s.replace('N','').replace('S','').replace('E','').replace('W','')
    parts = clean.split('-')
    try:
        if len(parts) >= 3:
            dd = float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600
        else:
            dd = float(clean)
        return round(dd * mult, 6)
    except: 
        return 0.0

def parse_dof_dms(dms_str):
    dms_str = dms_str.strip()
    if not dms_str: return 0.0
    direction = dms_str[-1]
    parts = dms_str[:-1].split()
    if len(parts) != 3: return 0.0
    decimal = float(parts[0]) + (float(parts[1]) / 60.0) + (float(parts[2]) / 3600.0)
    if direction in ['S', 'W']: decimal = -decimal
    return decimal

# --- NEW: NOTAM HARVESTER LOGIC (Version 2.0 MVP - Geography Search) ---

def harvest_notams():
    """
    MVP Scraper version of the NOTAM Harvester using Geography Search.
    Automated for headless servers (GitHub Actions) - No interactive prompts.
    """
    SEARCH_URL = "https://notams.aim.faa.gov/notamSearch/search"
    
    HEADERS_NOTAM = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # --- AUTOMATED GEOGRAPHY SEARCH CONFIG ---
    # Set your centerpoint identifier and search radius in Nautical Miles
    center_id = "KRDU" 
    search_radius = "150" 
    
    # Payload mimicking a web form "Geography Search"
    payload = (
        f"searchType=3"
        f"&radiusSearchOnDesignator=true"
        f"&radiusSearchDesignator={center_id}"
        f"&radius={search_radius}"
    )
    
    processed_notams = []
    print(f"[-] Scraping public NOTAMs for light outages within {search_radius}NM of {center_id}...")
    
    try:
        # 1. Fetch the data (simulating a web browser form submission)
        response = requests.post(SEARCH_URL, headers=HEADERS_NOTAM, data=payload, timeout=30)
        response.raise_for_status()
        
        # 2. Extract JSON or fallback to HTML table parsing
        notam_list = []
        try:
            notam_list = response.json().get('notamList', [])
        except ValueError:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            notam_list = [{'icaoMessage': cell.get_text()} for cell in soup.find_all('td')]
            
        # --- DIAGNOSTIC PRINT ---
        print(f"    > DIAGNOSTIC: FAA returned {len(notam_list)} total NOTAMs in this radius.")
            
        # 3. Regex Patterns
        keywords = ["OBST TOWER LGT", "OUT OF SERVICE", "U/S"]
        coord_pattern = r"(\d{2,3})(\d{2})(\d{2})([NS])\s?(\d{2,3})(\d{2})(\d{2})([EW])"
        agl_pattern = r"(\d+)\s?FT\s?AGL"

        for item in notam_list:
            text = item.get('icaoMessage', '')
            if not text:
                continue
                
            text = text.upper()
            
            # Filter for specific outage keywords
            if any(key in text for key in keywords):
                coords = re.search(coord_pattern, text)
                agl = re.search(agl_pattern, text)
                
                if coords:
                    lat = dms_to_dd_notam(coords.group(1), coords.group(2), coords.group(3), coords.group(4))
                    lon = dms_to_dd_notam(coords.group(5), coords.group(6), coords.group(7), coords.group(8))
                    
                    processed_notams.append({
                        "lat": lat,
                        "lon": lon,
                        "agl": agl.group(1) if agl else "Unknown",
                        "text": text
                    })
        
        with open("notams.json", 'w') as f:
            json.dump(processed_notams, f, indent=2)
        print(f"    > Scraped and saved {len(processed_notams)} NOTAM obstacles to notams.json.")
        
    except Exception as e:
        print(f"[!] NOTAM Scraper failed: {e}")

def dms_to_dd_notam(d, m, s, direction):
    """Specific converter for NOTAM DMS format."""
    dd = float(d) + float(m)/60 + float(s)/3600
    if direction in ['S', 'W']: dd *= -1
    return round(dd, 6)

def process_data():
    obstacles = []
    airports = {}
    metadata = {"dof_date": "Unknown", "apt_count": 0, "obs_count": 0}

    # --- 1. DOWNLOAD & PARSE DOF (56-Day Cycle) ---
    print("[-] Fetching latest DOF ZIP...")
    try:
        dof_zip_url = get_dof_zip_url()
        print(f"[-] Downloading: {dof_zip_url}")
        
        r_dof = requests.get(dof_zip_url, headers=HEADERS)
        with zipfile.ZipFile(io.BytesIO(r_dof.content)) as z:
            dat_filename = next(name for name in z.namelist() if name.upper().endswith('DOF.DAT'))
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
                        
                        lat = parse_dof_dms(line[35:47])
                        lon = parse_dof_dms(line[48:61])
                        city = line[18:34].strip()
                        state = line[15:17].strip().upper() # ADDED: 2-Letter State Code
                        oas = line[0:9].strip()
                        
                        obstacles.append({"id": oas, "state": state, "city": city, "lat": lat, "lon": lon, "agl": agl})
                    except:
                        continue
        print(f"    > Parsed {len(obstacles)} Obstacles.")
    except Exception as e:
        print(f"[!] DOF Process failed: {e}")

    # --- 2. DOWNLOAD & PARSE NASR APT (28-Day Cycle) ---
    print("\n[-] Fetching latest NASR APT ZIP...")
    cycle_date = get_current_airac_cycle()
    date_str = cycle_date.strftime("%Y-%m-%d")
    landing_url = f"https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/{date_str}"
    
    metadata["apt_date"] = cycle_date.strftime("%m/%d/%y")
    
    try:
        page_resp = requests.get(landing_url, headers=HEADERS, timeout=15)
        match = re.search(r'href=["\']([^"\']+\.zip)["\']', page_resp.text)
        if not match: match = re.search(r'href=["\'](https://[^"\']+\.zip)["\']', page_resp.text)
        
        if match:
            zip_url = match.group(1)
            if not zip_url.startswith("http"): zip_url = "https://www.faa.gov" + zip_url
            
            print(f"[-] Downloading: {zip_url}")
            r_nasr = requests.get(zip_url, headers=HEADERS, stream=True)
            
            with zipfile.ZipFile(io.BytesIO(r_nasr.content)) as z:
                apt_file_info = next(f for f in z.infolist() if f.filename.endswith('APT.txt'))
                with z.open(apt_file_info) as f:
                    for line_bytes in f:
                        line = line_bytes.decode('latin-1', errors='ignore')
                        if line.startswith("APT"):
                            loc_id = line[APT_COLS['id'][0]:APT_COLS['id'][1]].strip()
                            name_str = line[APT_COLS['name'][0]:APT_COLS['name'][1]].strip()
                            lat_str = line[APT_COLS['lat'][0]:APT_COLS['lat'][1]].strip()
                            lon_str = line[APT_COLS['lon'][0]:APT_COLS['lon'][1]].strip()
                            if loc_id and lat_str and lon_str:
                                lat = faa_to_decimal(lat_str)
                                lon = faa_to_decimal(lon_str)
                                if lat != 0.0 and lon != 0.0:
                                    airports[loc_id] = {"name": name_str, "lat": lat, "lon": lon}
            print(f"    > Parsed {len(airports)} Airports/Heliports.")
        else:
            print("[!] Could not find NASR ZIP link.")
    except Exception as e:
        print(f"[!] NASR Process failed: {e}")

    # --- 3. SAVE WITH FAILSAFE ---
    print("\n[-] Compiling outputs...")
    
    if len(obstacles) > 0:
        with open("obstacles.json", 'w') as f:
            json.dump(obstacles, f, separators=(',', ':'))
        metadata["obs_count"] = len(obstacles)
        print(f"[-] Saved {len(obstacles)} obstacles.")
    else:
        print("[!] WARNING: No obstacles parsed. Skipping overwrite to protect existing data.")
        if os.path.exists("obstacles.json"):
            try:
                with open("obstacles.json", 'r') as f:
                    metadata["obs_count"] = len(json.load(f))
            except: pass
            
    if len(airports) > 0:
        with open("airports.json", 'w') as f:
            json.dump(airports, f, separators=(',', ':'))
        metadata["apt_count"] = len(airports)
        print(f"[-] Saved {len(airports)} airports.")
        
    with open("metadata.json", 'w') as f:
        json.dump(metadata, f)
        
    # --- 4. NEW: NOTAM HARVEST (Version 2.0 MVP) ---
    harvest_notams()
        
    print("[-] Success. Database update complete.")

if __name__ == "__main__":
    process_data()