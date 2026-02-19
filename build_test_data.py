import json
import os

DOF_FILE = "DOF.DAT"
OUTPUT_JSON = "obstacles.json"

def parse_dms(dms_str):
    dms_str = dms_str.strip()
    if not dms_str: return 0.0
    direction = dms_str[-1]
    parts = dms_str[:-1].split()
    if len(parts) != 3: return 0.0
    decimal = float(parts[0]) + (float(parts[1]) / 60.0) + (float(parts[2]) / 3600.0)
    if direction in ['S', 'W']: decimal = -decimal
    return decimal

def main():
    obstacles = []
    with open(DOF_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if len(line) < 100 or line.startswith("CUR") or line.startswith("-") or line.startswith("OAS") or line.startswith(" "):
                continue
            try:
                agl_str = line[83:88].strip()
                if not agl_str.isdigit(): continue
                
                lat = parse_dms(line[35:47])
                lon = parse_dms(line[48:61])
                agl = int(agl_str)
                city = line[18:34].strip()
                oas = line[0:9].strip()
                
                obstacles.append({
                    "id": oas,
                    "city": city,
                    "lat": lat,
                    "lon": lon,
                    "agl": agl
                })
            except:
                continue
                
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(obstacles, f, separators=(',', ':'))
    print(f"Generated {OUTPUT_JSON} with {len(obstacles)} obstacles.")

if __name__ == "__main__":
    main()