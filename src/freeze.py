from flask_frozen import Freezer

from src.app import app

app.config["PREFERRED_URL_SCHEME"] = "https"
app.config["FREEZER_DESTINATION"] = "../build"
freezer = Freezer(app)


def main():
    freezer.freeze()


if __name__ == "__main__":
    main()
