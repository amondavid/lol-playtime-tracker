from flask import Flask
from database import init_db

app = Flask(__name__)

@app.route("/")
def index():
    return "LoL Playtime Tracker is Running."


def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()