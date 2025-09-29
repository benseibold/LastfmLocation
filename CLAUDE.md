# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

LastfmLocation is a personal data analytics project that combines Last.fm music listening history with Google Location History and SMS data to create visualizations showing where music was listened to and a digital journal timeline of activities.

## Key Components

### Python Scripts

**MusicMap.py** - Main music-location analysis script
- Processes Google Location History JSON files from `Data\GoogleData1-1-2020\Location History\Semantic Location History\{year}`
- Reads Last.fm listening history from `Data\lastfm.csv` (format: artist, album, song, date)
- Uses bisect algorithm to match songs to locations by timestamp
- Generates interactive Plotly map showing top songs played at each location
- Filters to only show locations with >20 songs played
- Creates ranked list of top 4 songs per location

**DigitalJournal.py** - Timeline visualization script
- Combines Google Location History, SMS data (XML), and Last.fm data
- Processes location data into simplified format with activitySegment and placeVisit types
- Parses SMS XML from `Data/SmsDataTest.xml`
- Generates `react/site/src/data.json` for the React frontend
- Sorts all events chronologically by timestamp

### React Frontend

Located in `react/site/` - Create React App project that displays digital journal timeline
- Renders cards for place visits, activities, and text messages in chronological order
- Groups messages by day with date headers
- Displays contact names and message direction (sent/received)

## Data Structure

The project expects this data layout:
- `Data/lastfm.csv` - Last.fm scrobble history
- `Data/SmsDataTest.xml` - SMS backup in XML format
- `Data/GoogleData1-1-2020/Location History/Semantic Location History/{year}/*.json` - Google Timeline JSON exports
- `Data/GoogleData1-1-2020/Google Photos/` - Google Photos metadata JSON files

Timestamps are converted to Unix epoch milliseconds for consistency across data sources.

## Common Commands

### Python Scripts
```bash
python MusicMap.py          # Generate music location map
python DigitalJournal.py    # Generate timeline data for React app
```

### React Development
```bash
cd react/site
npm start                   # Start development server
npm run build              # Build for production
npm test                   # Run tests
```

## Development Notes

- Python 3.8+ required (uses pandas, plotly, xml.etree)
- Google Location History data uses E7 format for coordinates (divide by 10000000)
- SMS XML attributes: body, date, type (1=received, 2=sent), contact_name
- The bisect matching algorithm in MusicMap.py may have timestamp sync issues between Last.fm and Google data
- React app filters data to specific date ranges in `jsonToFile()` function