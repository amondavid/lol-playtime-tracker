from flask import Flask, render_template, request, redirect
from database import init_db, save_setting, get_setting
from riot_api import get_account_by_riot_id, RiotApiError

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

def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()