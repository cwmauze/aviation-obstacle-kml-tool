# Contributing to KML Obstacle Tool

First off, thanks for taking the time to contribute! This tool relies on community feedback to ensure it meets the practical needs of pilots and flight planners.

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please create an issue in the repository. Make sure you include:
- Your operating system and browser.
- The specific search parameters that caused the bug.
- Any errors that appeared in your browser's developer console.

### Suggesting Enhancements
Have an idea for a new feature? We'd love to hear it! Open an issue describing the feature, why it would be useful, and how you imagine it working.

### Pull Requests
We gladly accept pull requests! 
1. **Fork the repo** and create your branch from `main`.
2. **Make your changes** in your local environment.
3. **Test your changes** to ensure you didn't break existing parsing or UI logic.
4. **Issue the PR**, explaining what you did and why.

## Local Development Setup

Because of the new automated deployment strategy, the heavy JSON database files (`obstacles.json`, `airports.json`, `notams.json`) are no longer stored in the repository.

To test the application locally, you will need to generate these files yourself:

1. Clone the repository.
2. Install the required Python dependencies: `pip install -r requirements.txt`.
3. Run the database script: `python scripts/update_database.py`. 
   - *Note: To test the NOTAM parsing locally, you will need to set `FAA_CLIENT_ID` and `FAA_CLIENT_SECRET` environment variables. If these are not present, the script will gracefully skip the NOTAM section.*
4. Use a local server (like the VS Code Live Server extension or `python -m http.server 8000`) to run `index.html`. Browsers block local file access for `fetch()` requests, so you *must* use a local web server to test the tool.

## Code Style
- **Python**: Try to stick to PEP 8 where reasonable.
- **HTML/JS**: Keep logic contained in the `index.html` file to maintain the single-file simplicity of the frontend (for now). Use standard modern JavaScript (ES6+).
