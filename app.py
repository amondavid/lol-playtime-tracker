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

    return render_template(
    "settings.html",
    settings=load_settings(),
    success_message=None,
    error_message=None,
)


@app.route("/test-account", methods=["POST"])
def test_account():
    try:
        account_data = get_account_by_riot_id()
    except RiotApiError as error:
        return render_template(
            "settings.html",
            settings=load_settings(),
            success_message=None,
            error_message=f"Riot API error: {error}",
        )

    return render_template(
        "settings.html",
        settings=load_settings(),
        success_message=(
            f"Connected successfully as "
            f"{account_data['game_name']}#{account_data['tagline']}."
        ),
        error_message=None,
    )


@app.route("/import-recent-matches", methods=["POST"])
def import_recent_matches():
    target_import_count = 20
    batch_size = 20
    max_matches_to_check = 100

    imported_count = 0
    skipped_count = 0
    checked_count = 0

    try:
        start = 0

        while imported_count < target_import_count and checked_count < max_matches_to_check:
            match_ids = get_recent_match_ids(start=start, count=batch_size)

            if not match_ids:
                break

            for match_id in match_ids:
                if imported_count >= target_import_count:
                    break

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

            start += batch_size

    except RiotApiError as error:
        return render_riot_error(error)

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


def load_settings():
    return {
        "riot_id": get_setting("riot_id") or "",
        "tagline": get_setting("tagline") or "",
        "region": get_setting("region") or "",
        "api_key": get_setting("api_key") or "",
    }


def render_riot_error(error):
    return (
        render_template(
            "error.html",
            error_message=f"Riot API error: {error}",
        ),
        400,
    )

def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()

