# LoL Playtime Tracker

A small local Python app that tracks imported League of Legends playtime using Riot match history data.

## Goal

This project lets me:

- save a Riot ID, tagline, region, and API key locally
- fetch available match history from Riot's API
- store match data in a local SQLite database
- calculate simple playtime stats
- view the stats in a small local Flask interface

## Important notes

This is a personal local learning project, not a public product.

"Total playtime" means total imported playtime from available match data. It may not equal true lifetime League of Legends playtime.

## Planned stack

- Python
- Flask
- SQLite
- requests
- pytest later
