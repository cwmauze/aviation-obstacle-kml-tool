# Roadmap

This roadmap outlines the planned features, improvements, and architectural changes for the KML Obstacle Tool.

## Short-Term Goals (Next Release)
- **CI/CD Stabilization**: Monitor the new GitHub Actions workflow deploying to GitHub Pages to ensure reliability of the database updates.
- **Data Pruning**: Optimize the database creation script to strip out any unused attributes to further shrink the `.json` file sizes and improve browser loading speed.
- **Improved Caching**: Add stronger Service Worker caching for the map tiles and static assets so the app loads faster in low-connectivity environments.
- **UI/UX Modernization**: Overhaul the interface with a modern, responsive design system (incorporating dark mode for low-light aviation environments).
- **Enhanced Filtering**: Add the ability to filter obstacles by specific types (e.g., wind turbines, radio towers, buildings) utilizing detailed DOF data.

## Medium-Term Goals (Next 6 Months)
- **Route-Based Corridors**: Evolve beyond single centerpoints by allowing users to input a sequence of waypoints to generate an obstacle overlay for an entire flight route/corridor. NOTE: Don't we already have this?
- **Expanded Coverage**: Consider pulling Canadian and Mexican obstacle datasets to support cross-border route planning.
- **Performance Optimization**: Implement web workers to handle the KML generation logic so the UI doesn't freeze when calculating thousands of coordinates.
- **Offline Support (PWA)**: Make the tool a Progressive Web App (PWA) so users can generate overlays on their iPad even without cell service.
- **Custom User Obstacles**: Allow users to manually drop pins or input coordinates for temporary or uncharted obstacles not yet in the FAA database. NOTE: I am not sure we need this, there are already mapping tools that do this.
- **Multi-Format Export**: Support additional export formats like GeoJSON to support a wider range of mapping tools and GIS software beyond KML.

## Long-Term Vision
- **3D Visualization**: Allow previewing the generated paths and obstacles in a 3D environment directly within the browser using tools like CesiumJS.
- **Dynamic Terrain Integration**: Incorporate digital elevation models (DEM) to allow MSL filtering based on local terrain, rather than just raw AGL values.
- **Cloud Sync & Profiles**: Introduce a lightweight backend (e.g., Firebase) to allow users to sync templates and preferred settings across multiple devices.
- **Direct EFB Integration**: Work on finding ways to directly push generated KMLs to common EFB apps via local network APIs instead of requiring a manual file download.

*Community input is always welcome. If you have a feature request, please open an issue!*
