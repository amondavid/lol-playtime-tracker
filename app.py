from flask import Flask, render_template, request, redirect
from database import init_db, save_setting, get_setting, save_match, get_playtime_stats
from riot_api import (
    get_account_by_riot_id, 
    get_recent_match_ids,
    get_match_by_id, 
    RiotApiError
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

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


@app.route("/import-recent-matches")
def import_recent_matches():
    try:
        match_ids = get_recent_match_ids(count=5)

        imported_count = 0
        skipped_count = 0

        for match_id in match_ids:
            match_data = get_match_by_id(match_id)
            info = match_data["info"]

            inserted = save_match(
                match_data["metadata"]["matchId"],
                info["gameStartTimestamp"],
                info["gameDuration"],
                info["queueId"],
            )

            if inserted:
                imported_count += 1
            else:
                skipped_count += 1

    except RiotApiError as error:
        return f"Riot API error: {error}", 400

    return (
        "<h1>Import complete</h1>"
        f"<p>Imported: {imported_count}</p>"
        f"<p>Skipped duplicates: {skipped_count}</p>"
        f"<p>Checked: {len(match_ids)} matches</p>"
    )


@app.route("/stats")
def stats():
    stats_data = get_playtime_stats()

    total_playtime = format_seconds(stats_data["total_seconds"])
    last_14_days_playtime = format_seconds(stats_data["last_14_days_seconds"])

    return (
        "<h1>Playtime Stats</h1>"
        f"<p>Total imported matches: {stats_data['total_matches']}</p>"
        f"<p>Total imported playtime: {total_playtime}</p>"
        f"<p>Playtime in last 14 days: {last_14_days_playtime}</p>"
    )


def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    return f"{hours}h {minutes}m"

def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()

