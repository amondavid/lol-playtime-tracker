# LoL Playtime Tracker

A small local Flask app for tracking League of Legends playtime from imported Riot match history data.

The app saves Riot account settings locally, fetches match data from Riot’s API, stores matches in SQLite, and calculates playtime stats from the stored data. It also shows the date of the last time the game was played.

## Features

- Save Riot ID, tagline, region, and Riot API key locally
- Test the saved Riot connection
- Update playtime from Riot match history
- Store imported matches in SQLite
- Skip duplicate matches
- Show:
  - total imported matches
  - total imported playtime
  - playtime in the last 14 days

## Tech Stack

- Python
- Flask
- Jinja
- SQLite
- `sqlite3`
- `requests`
- HTML/CSS

## How It Works

```text
Riot ID + tagline
→ PUUID
→ match IDs
→ match details
→ SQLite
→ playtime stats
```

Riot does not provide one direct “total playtime” value. This app calculates playtime by storing imported match durations and summing them locally.

“Total imported playtime” means playtime from matches currently stored in the local database, not guaranteed lifetime League of Legends playtime.

## Setup

Clone the repository:

```bash
git clone <repository-url>
cd lol-playtime-tracker
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Riot API Key

This app needs a Riot API key to fetch match data.

For local development, sign in to the Riot Developer Portal with a Riot account and use the development API key from the dashboard.

Development keys are temporary and need to be regenerated regularly. For longer-term personal use, register the project in the Developer Portal and apply for a personal API key.

Do not commit your Riot API key to Git.

## Settings

On the settings page, enter:

- Riot ID
- Tagline
- Region
- Riot API key

Example:

```text
Riot ID: GameName
Tagline: Tagline
Region: europe
```

Use a regional routing value such as `europe`, not a platform value like `EUW1`.

## Local Data

The app creates a local SQLite database in the `data/` directory.

Local data and secrets should not be committed. The project ignores files such as:

```text
data/
*.db
.env
.venv/
```

## Limitations

- Requires a Riot API key
- Development API keys expire and may need to be regenerated
- Riot API rate limits affect updates
- Playtime depends on available/imported match history
- Built for local personal use, not public deployment
