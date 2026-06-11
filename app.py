from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "LoL Playtime Tracker is Running."


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()