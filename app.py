from flask import Flask, render_template, request, redirect
from database import init_db, save_setting, get_setting, save_match
from riot_api import (
    get_account_by_riot_id, 
    get_recent_match_ids,
    get_match_by_id, 
    RiotApiError
)

app = Flask(__name__)


@app.route("/")
def index():
    return "LoL Playtime Tracker is Running."

@app.route("/settings", methods=['GET', "POST"])
def settings():
    if request.method == "POST":
        save_setting("riot_id", request.form.get("riot_id", ""))
        save_setting("tagline", request.form.get("tagline", ""))
        save_setting("region", request.form.get("region", ""))
        save_setting("api_key", request.form.get("api_key", ""))

        return redirect("/settings")

    settings = {
        "riot_id": get_setting("riot_id") or "",
        "tagline": get_setting("tagline") or "",
        "region": get_setting("region") or "",
        "api_key": get_setting("api_key") or "",
    }

    return render_template("settings.html", settings=settings)


@app.route("/account")
def account():
    try:
        account_data = get_account_by_riot_id()
    except RiotApiError as error:
        return f"Riot API error {error}", 400
    
    return (
        f"Found account: {account_data['game_name']}#{account_data['tagline']}"
        f"<br>PUUID: {account_data['puuid']}"
    )


@app.route("/matches")
def matches():
    try:
        match_ids = get_recent_match_ids()
    except RiotApiError as error:
        return f"Riot API error: {error}", 400

    html = "<h1>Recent match IDs</h1>"
    html += "<ul>"

    for match_id in match_ids:
        html += f"<li>{match_id}</li>"

    html += "</ul>"

    return html


@app.route("/latest-match")
def latest_match():
    try:
        match_ids = get_recent_match_ids(count=1)
        match_data = get_match_by_id(match_ids[0])
    except RiotApiError as error:
        return f"Riot API error: {error}", 400

    info = match_data["info"]

    return (
        "<h1>Latest match</h1>"
        f"<p>Match ID: {match_data['metadata']['matchId']}</p>"
        f"<p>Game duration: {info['gameDuration']} seconds</p>"
        f"<p>Game start timestamp: {info['gameStartTimestamp']}</p>"
        f"<p>Queue ID: {info['queueId']}</p>"
    )


@app.route("/import-latest-match")
def import_latest_match():
    try:
        match_ids = get_recent_match_ids(count=1)
        match_data = get_match_by_id(match_ids[0])
    except RiotApiError as error:
        return f"Riot API error: {error}", 400

    info = match_data["info"]

    match_id = match_data["metadata"]["matchId"]
    game_start_timestamp = info["gameStartTimestamp"]
    game_duration_seconds = info["gameDuration"]
    queue_id = info["queueId"]

    save_match(
        match_id,
        game_start_timestamp,
        game_duration_seconds,
        queue_id,
    )

    return (
        "<h1>Imported latest match</h1>"
        f"<p>Match ID: {match_id}</p>"
        f"<p>Duration: {game_duration_seconds} seconds</p>"
        f"<p>Started at: {game_start_timestamp}</p>"
        f"<p>Queue ID: {queue_id}</p>"
    )

def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()
