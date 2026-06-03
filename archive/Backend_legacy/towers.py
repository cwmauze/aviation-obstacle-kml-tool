import math
import os

# --- CONFIGURATION ---
CENTER_LAT = 36.0066   # Duke University Medical Center Latitude
CENTER_LON = -78.9391  # Duke University Medical Center Longitude
RADIUS_NM = 150.0      # Search radius in Nautical Miles
CIRCLE_RADIUS_SM = 2.0 # Polygon ring radius in Statute Miles
MIN_AGL = 1000         # Minimum AGL height to include

DOF_FILE = "DOF.DAT"   # Path to your downloaded FAA DOF file
OUTPUT_KML = "Duke_Towers_1000_AGL.kml"

def parse_dms(dms_str):
    """Converts FAA DOF lat/lon format (e.g., '35 45 12.34N') to decimal degrees."""
    dms_str = dms_str.strip()
    if not dms_str:
        return 0.0
    
    direction = dms_str[-1]
    parts = dms_str[:-1].split()
    if len(parts) != 3:
        return 0.0
        
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def haversine_nm(lat1, lon1, lat2, lon2):
    """Calculates distance between two points in Nautical Miles."""
    R = 3440.065  # Earth radius in NM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_circle_coords(lat, lon, radius_sm, num_points=36):
    """Generates KML coordinate string for a circle around a point."""
    coords = []
    earth_radius_sm = 3958.8
    d_rad = radius_sm / earth_radius_sm
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    for i in range(num_points):
        angle = math.radians(float(i) / num_points * 360.0)
        new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(d_rad) + 
                                math.cos(lat_rad) * math.sin(d_rad) * math.cos(angle))
        new_lon_rad = lon_rad + math.atan2(math.sin(angle) * math.sin(d_rad) * math.cos(lat_rad), 
                                           math.cos(d_rad) - math.sin(lat_rad) * math.sin(new_lat_rad))
        
        coords.append(f"{math.degrees(new_lon_rad)},{math.degrees(new_lat_rad)},0")
        
    # Close the polygon loop
    coords.append(coords[0])
    return " ".join(coords)

def main():
    if not os.path.exists(DOF_FILE):
        print(f"Error: Could not find '{DOF_FILE}'. Please download it from the FAA website.")
        return

    # KML Header matching your original file's style tags
    kml_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        '\t<name>~Towers &gt; 1000 AGL Duke</name>',
        '\t<description>2SM ring surrounding all towers within 150NM radius of Duke University Medical Center that are &gt; 1000\' AGL.</description>',
        '\t<Style id="redCircle">',
        '\t\t<LineStyle>',
        '\t\t\t<color>ff0000ff</color>',
        '\t\t\t<width>2</width>',
        '\t\t</LineStyle>',
        '\t\t<PolyStyle>',
        '\t\t\t<color>802e00ff</color>',
        '\t\t\t<fill>0</fill>',
        '\t\t</PolyStyle>',
        '\t</Style>'
    ]

    towers_found = 0

    with open(DOF_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Skip headers and short lines
            if len(line) < 100 or line.startswith("CUR") or line.startswith("-") or line.startswith("OAS") or line.startswith(" "):
                continue
                
            try:
                # Extract AGL height
                agl_str = line[83:88].strip()
                if not agl_str.isdigit():
                    continue
                
                agl = int(agl_str)
                if agl <= MIN_AGL:
                    continue
                    
                # Extract Lat/Lon coordinates
                lat_str = line[35:47]
                lon_str = line[48:61]
                tower_lat = parse_dms(lat_str)
                tower_lon = parse_dms(lon_str)
                
                # Check distance from Duke
                dist = haversine_nm(CENTER_LAT, CENTER_LON, tower_lat, tower_lon)
                if dist <= RADIUS_NM:
                    city = line[18:34].strip()
                    oas = line[0:9].strip()
                    
                    circle_coords = generate_circle_coords(tower_lat, tower_lon, CIRCLE_RADIUS_SM)
                    
                    # Build KML Placemark
                    kml_content.append('\t<Placemark>')
                    kml_content.append(f'\t\t<name>{city} ({oas})</name>')
                    kml_content.append('\t\t<styleUrl>#redCircle</styleUrl>')
                    kml_content.append('\t\t<Polygon>')
                    kml_content.append('\t\t\t<outerBoundaryIs>')
                    kml_content.append('\t\t\t\t<LinearRing>')
                    kml_content.append(f'\t\t\t\t\t<coordinates>\n\t\t\t\t\t\t{circle_coords}\n\t\t\t\t\t</coordinates>')
                    kml_content.append('\t\t\t\t</LinearRing>')
                    kml_content.append('\t\t\t</outerBoundaryIs>')
                    kml_content.append('\t\t</Polygon>')
                    kml_content.append('\t</Placemark>')
                    
                    towers_found += 1

            except Exception:
                continue # Skip rows that have formatting anomalies 

    kml_content.append('</Document>\n</kml>')

    with open(OUTPUT_KML, 'w') as f:
        f.write("\n".join(kml_content))

    print(f"Success! Generated '{OUTPUT_KML}' with {towers_found} towers.")

if __name__ == "__main__":
    main()