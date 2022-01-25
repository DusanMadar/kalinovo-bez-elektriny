from datetime import datetime
import json
from pathlib import Path

from flask import Flask, render_template
from flask_htmlmin import HTMLMIN
from flask_pretty import Prettify


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


minify_html = True
# minify_page = False
app.config["MINIFY_PAGE"] = minify_html
app.config["PRETTIFY"] = not minify_html
app.jinja_env.add_extension("jinja2.ext.do")
Prettify(app)
HTMLMIN(app)


@app.route("/")
def index():
    with open(Path(__file__).parent.parent.absolute().joinpath("data.json"), "r") as fd:
        data = json.load(fd)
    return render_template(
        "index.html", data=data, updated_at=datetime.now().isoformat(" ", "minutes")
    )


if __name__ == "__main__":
    app.run(debug=True)
