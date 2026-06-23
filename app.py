from flask import Flask, render_template, request, redirect

from database import (
    init_db,
    save_setting,
    get_setting,
    save_match,
    match_exists,
    get_playtime_stats,
)

from riot_api import (
    get_account_by_riot_id, 
    get_recent_match_ids,
    get_match_by_id, 
    RiotApiError
)

app = Flask(__name__)


@app.route("/")
def index():
    stats_data = get_playtime_stats()

    return render_template(
        "index.html",
        total_matches=stats_data["total_matches"],
        total_playtime=format_seconds(stats_data["total_seconds"]),
        last_14_days_playtime=format_seconds(stats_data["last_14_days_seconds"]),
    )

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



@app.route("/import-recent-matches", methods=["POST"])
def import_recent_matches():
    max_matches = 20
    batch_size = 20

    imported_count = 0
    skipped_count = 0
    checked_count = 0

    try:
        for start in range(0, max_matches, batch_size):
            match_ids = get_recent_match_ids(start=start, count=batch_size)

            if not match_ids:
                break

            for match_id in match_ids:
                checked_count += 1

                if match_exists(match_id):
                    skipped_count += 1
                    continue

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

    return render_template(
        "import_result.html",
        imported_count=imported_count,
        skipped_count=skipped_count,
        checked_count=checked_count,
    )


@app.route("/stats")
def stats():
    stats_data = get_playtime_stats()

    return render_template(
        "stats.html",
        total_matches=stats_data["total_matches"],
        total_playtime=format_seconds(stats_data["total_seconds"]),
        last_14_days_playtime=format_seconds(stats_data["last_14_days_seconds"]),
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

