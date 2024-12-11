# Spotify Playlist and Artist Data Extractor

This script streamlines the **extraction and organization of data from Spotify's "Daily Top 50 Tracks" playlists across 74 countries**, along with detailed information about the associated artists. Leveraging the Spotipy library and anonymous API access via SpotifyAnon, it automates the entire workflow: downloading playlist data, transforming it into structured formats, and retrieving comprehensive artist metadata for seamless analysis.

## Features
- **Playlist Data Extraction**: Downloads data from Spotify playlists listed in an Excel file (`playlist.xlsx`), saving it in JSON format.
- **Data Parsing**: Converts raw playlist data into structured Excel files, including track details (e.g., artist names, album info, popularity).
- **Artist Info Retrieval**: Fetches detailed artist metadata (e.g., genres, followers, popularity) for all unique artists found in the playlists.
- **Consolidated Data**: Merges all playlist and artist information into a single Excel file for easy analysis.

## How It Works
1. **Playlist Extraction**:
   - Reads playlist IDs from `playlist.xlsx`.
   - Queries the Spotify API for each playlist's items.
   - Saves the raw data as JSON files in `raw_data/<date>/playlist_items/`.

2. **Parsing Playlist Data**:
   - Converts JSON files to Excel format.
   - Extracts detailed track information (e.g., artist, duration, explicit content).
   - Combines all playlists into a single Excel file.

3. **Fetching Artist Information**:
   - Collects unique artist IDs from the playlist data.
   - Retrieves artist metadata via the Spotify API, including genres and follower counts.
   - Saves individual artist data as Excel files and merges it with the playlist data.

4. **Output**:
   - The final Excel file, located in `raw_data/<date>/`, contains consolidated information on tracks and their associated artists.

## Requirements
- Python 3.8+
- Libraries: `spotipy`, `pandas`, `openpyxl`, `tqdm`
- `playlist.xlsx` file with columns:
  - `COUNTRY`: Country of the playlist.
  - `ID`: Spotify playlist ID.
  - `NAME`: Playlist name.

## Usage
1. Install dependencies:
   ```bash
   pip install spotipy pandas openpyxl tqdm
   ```

**Ensure playlist.xlsx is in the script's directory!**

