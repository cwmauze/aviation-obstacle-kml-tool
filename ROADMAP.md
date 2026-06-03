# Roadmap

This roadmap outlines the planned features, improvements, and architectural changes for the KML Obstacle Tool.

## Short-Term Goals (Next Release)
- **CI/CD Stabilization**: Monitor the new GitHub Actions workflow deploying to GitHub Pages to ensure reliability of the database updates.
- **Data Pruning**: Optimize the database creation script to strip out any unused attributes to further shrink the `.json` file sizes and improve browser loading speed.
- **Improved Caching**: Add stronger Service Worker caching for the map tiles and static assets so the app loads faster in low-connectivity environments.

## Medium-Term Goals (Next 6 Months)
- **Expanded Coverage**: Consider pulling Canadian and Mexican obstacle datasets to support cross-border route planning.
- **Performance Optimization**: Implement web workers to handle the KML generation logic so the UI doesn't freeze when calculating thousands of coordinates.
- **Offline Support**: Make the tool a Progressive Web App (PWA) so users can generate overlays on their iPad even without cell service.

## Long-Term Vision
- **3D Visualization**: Allow previewing the generated paths and obstacles in a 3D environment directly within the browser using tools like CesiumJS.
- **Direct EFB Integration**: Work on finding ways to directly push generated KMLs to common EFB apps via local network APIs instead of requiring a manual file download.

*Community input is always welcome. If you have a feature request, please open an issue!*
