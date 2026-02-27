# KML Obstacle Overlay Generator

A lightweight, browser-based tool to generate custom KML obstacle overlays for ForeFlight, Google Earth, and other Electronic Flight Bags (EFBs) that support KML imports.

## Why does this exist?
Because the NAS is filled with tall, pointy things, NOTAMs are perpetually flooded with "OBST LGT OUT OF SERVICE" warnings, and hitting a 1,500-foot radio tower in the dark is generally considered poor airmanship. This tool allows you to easily pull current FAA obstacle data, filter it to your specific mission parameters, and visualize it natively in your EFB.

## Features
* **Smart Centerpoints:** Search by 3 or 4-letter FAA identifier (e.g., `RDU` or `KABQ`) or input custom decimal Lat/Lon coordinates.
* **Custom Filtering:** Set your own search radius (NM) and minimum obstacle height (AGL) to filter out the noise.
* **Live NOTAM Integration:** Automatically pulls and visualizes active nationwide obstacle NOTAMs alongside static DOF data.
* **Template Saving & Loading:** Save your specific search parameters, centerpoints, and visual overlay options as a local template file. Re-upload it later to instantly recreate your custom KML overlay using the most up-to-date database.
* **Visual Styling:** Tweak the color, line thickness, ring radius, and fill opacity of the obstacle markers so they look exactly how you want them to on your chart.
* **Map Preview:** Visually validate your overlay directly in the browser against Street, Satellite, or actual FAA VFR Sectional charts before exporting.
* **Automated Database Sync:** The backend uses a GitHub Action to automatically scrape, parse, and verify the FAA's 56-Day Digital Obstacle File (DOF), 28-Day NASR Airport databases, and live NMS-API NOTAMs.

## How it Works
The frontend application is entirely client-side. The HTML/JS interface reads from a set of lightweight, pre-parsed JSON databases (`obstacles.json`, `airports.json`, `notams.json`, `metadata.json`).

The heavy lifting is handled by a backend Python script (`update_database.py`) that runs automatically via GitHub Actions. It navigates the FAA Aeronav portals and the FAA NMS-API, extracts the massive `.DAT` and `.txt` files directly into memory, crunches the coordinates using regular expressions, pulls live NOTAMs, updates the local JSON files, and silently pushes the updates to the live site. 

## Usage
1. Open the [live GitHub Pages link](https://cwmauze.github.io/aviation-obstacle-kml-tool//).
2. Verify the Database Status card shows the data is current and verified.
3. Enter your centerpoint (FAA ID or coordinates) and desired radius.
4. Set your minimum AGL (e.g., if you are flying at 1,500' AGL, you might only care about obstacles > 1,000' AGL).
5. Adjust your ring sizes and colors. 
6. *(Optional)* Click **Save Template** to keep these settings for future use, or click **Load Template** to restore a previous configuration.
7. Click **Preview .KML** to check your work on the VFR sectional.
8. Click **Download .KML** and drop the file into ForeFlight via AirDrop, email, or a connected drive.

## Disclaimer
**This tool is for utility purposes only and is not a substitute for a qualified pilot or common sense.** While the database is meticulously parsed directly from the FAA, cumulus granite and steel towers remain strictly unforgiving. Generating a colorful KML file does not grant you invincibility. Cross-reference official charts, read your NOTAMs, and don't hit stuff.