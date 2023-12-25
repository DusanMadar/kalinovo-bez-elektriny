import json
from collections import defaultdict
from datetime import date, datetime
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

    yearly_data = defaultdict(dict)
    for date_, times in data.items():
        year = date_.split("-")[0]
        yearly_data[int(year)][date_] = times

    yearly_totals = {}
    weekdays = ["Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota", "Nedeľa"]

    for year, daily_data in yearly_data.items():
        months = set()
        weekday_count = {weekday: 0 for weekday in weekdays}
        for date_, data in daily_data.items():
            months.add(date_.split("-")[1])
            weekday = date.fromisoformat(date_).weekday()
            weekday_count[weekdays[weekday]] += len(data)

        total_count = 0
        time_ranges = defaultdict(int)
        for data in daily_data.values():
            total_count += len(data)
            for outage_start, _ in data:
                if "00:00:00" <= outage_start <= "06:00:00":
                    key= "night"
                elif "06:00:01" <= outage_start <= "12:00:00":
                    key = "morning"
                elif "12:00:01" <= outage_start <= "18:00:00":
                    key = "day"
                elif "18:00:01" <= outage_start:
                    key = "evening"

                time_ranges[key] += 1

        monthly_average = round(total_count / len(months), 2)
        monthly_average = (
            monthly_average if not monthly_average.is_integer() else int(monthly_average)
        )
        yearly_totals[year] = {
            "days": len(daily_data),
            "count": total_count,
            "monthly_average": monthly_average,
            "time_ranges": time_ranges,
            "weekday_count": weekday_count,

        }

    now = datetime.now()
    return render_template(
        "index.html",
        yearly_data=yearly_data,
        yearly_totals=yearly_totals,
        current_year=now.year,
        updated_at=now.isoformat(" ", "minutes"),
    )


if __name__ == "__main__":
    app.run(debug=True)
