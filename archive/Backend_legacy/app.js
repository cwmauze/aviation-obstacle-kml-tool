// Convert standard HTML Hex (#RRGGBB) to KML Color Format (AABBGGRR)
function hexToKmlColor(hex, opacityHex) {
    hex = hex.replace('#', '');
    const r = hex.substring(0, 2);
    const g = hex.substring(2, 4);
    const b = hex.substring(4, 6);
    return `${opacityHex}${b}${g}${r}`; 
}

// Calculate distance in Nautical Miles
function haversineNM(lat1, lon1, lat2, lon2) {
    const R = 3440.065; 
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Generate the polygon coordinates for the circle
function generateCircleCoords(lat, lon, radiusSM) {
    const coords = [];
    const earthRadiusSM = 3958.8;
    const dRad = radiusSM / earthRadiusSM;
    const latRad = lat * Math.PI / 180;
    const lonRad = lon * Math.PI / 180;

    for (let i = 0; i <= 36; i++) {
        const angle = (i === 36 ? 0 : i) / 36.0 * 2 * Math.PI;
        const newLatRad = Math.asin(Math.sin(latRad) * Math.cos(dRad) + Math.cos(latRad) * Math.sin(dRad) * Math.cos(angle));
        const newLonRad = lonRad + Math.atan2(Math.sin(angle) * Math.sin(dRad) * Math.cos(latRad), Math.cos(dRad) - Math.sin(latRad) * Math.sin(newLatRad));
        coords.push(`${newLonRad * 180 / Math.PI},${newLatRad * 180 / Math.PI},0`);
    }
    return coords.join(" ");
}

async function generateKML() {
    const centerLat = parseFloat(document.getElementById('lat').value);
    const centerLon = parseFloat(document.getElementById('lon').value);
    const searchRadiusNM = parseFloat(document.getElementById('radiusNM').value);
    const minAGL = parseInt(document.getElementById('minAGL').value);
    const ringRadiusSM = parseFloat(document.getElementById('ringSM').value);
    
    // Process Colors (KML requires AABBGGRR. Opacity FF = 100%, 80 = 50% transparent)
    const outlineColor = hexToKmlColor(document.getElementById('outlineColor').value, 'ff');
    const fillColor = hexToKmlColor(document.getElementById('fillColor').value, '80');
    const enableFill = document.getElementById('enableFill').checked ? '1' : '0';

    try {
        // Fetch the local JSON file
        const response = await fetch('obstacles.json');
        const obstacles = await response.json();
        
        let kml = `<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n`;
        kml += `\t<name>Obstacles > ${minAGL} AGL</name>\n`;
        kml += `\t<Style id="customCircle">\n\t\t<LineStyle>\n\t\t\t<color>${outlineColor}</color>\n\t\t\t<width>2</width>\n\t\t</LineStyle>\n`;
        kml += `\t\t<PolyStyle>\n\t\t\t<color>${fillColor}</color>\n\t\t\t<fill>${enableFill}</fill>\n\t\t</PolyStyle>\n\t</Style>\n`;

        let count = 0;

        // Filter obstacles and generate placemarks
        obstacles.forEach(obs => {
            if (obs.agl > minAGL) {
                const dist = haversineNM(centerLat, centerLon, obs.lat, obs.lon);
                if (dist <= searchRadiusNM) {
                    const circleCoords = generateCircleCoords(obs.lat, obs.lon, ringRadiusSM);
                    kml += `\t<Placemark>\n\t\t<name>${obs.city} (${obs.id}) - ${obs.agl} AGL</name>\n\t\t<styleUrl>#customCircle</styleUrl>\n`;
                    kml += `\t\t<Polygon>\n\t\t\t<outerBoundaryIs>\n\t\t\t\t<LinearRing>\n\t\t\t\t\t<coordinates>\n\t\t\t\t\t\t${circleCoords}\n\t\t\t\t\t</coordinates>\n\t\t\t\t</LinearRing>\n\t\t\t</outerBoundaryIs>\n\t\t</Polygon>\n\t</Placemark>\n`;
                    count++;
                }
            }
        });

        kml += `</Document>\n</kml>`;

        // Trigger Download
        const blob = new Blob([kml], { type: 'application/vnd.google-earth.kml+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Obstacles_${minAGL}AGL_${searchRadiusNM}NM.kml`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert(`Success! Generated KML with ${count} obstacles.`);

    } catch (error) {
        console.error("Error generating KML:", error);
        alert("Make sure you are running this on a web server (like GitHub Pages or VS Code Live Server) so it can load the obstacles.json file!");
    }
}