from collections import defaultdict
from datetime import date, datetime

from flask import Flask, render_template
from flask_htmlmin import HTMLMIN
from flask_pretty import Prettify

from src.utils import csv_to_dict

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


minify_html = True
# minify_page = False
app.config["MINIFY_PAGE"] = minify_html
app.config["PRETTIFY"] = not minify_html
app.jinja_env.add_extension("jinja2.ext.do")
Prettify(app)
HTMLMIN(app)

WEEKDAYS = ["Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota", "Nedeľa"]


@app.route("/")
def index():
    data = csv_to_dict()

    per_year_outages = defaultdict(dict)
    for date_, daily_data in data.items():
        year = int(date_.split("-")[0])
        per_year_outages[year][date_] = daily_data

    per_year_outages_agg = {}
    for year, daily_data in per_year_outages.items():
        total_count = 0
        weekday_count = {weekday: 0 for weekday in WEEKDAYS}
        time_ranges = {
            "00:00 - 06:00": 0,
            "06:01 - 12:00": 0,
            "12:01 - 18:00": 0,
            "18:01 - 23:59": 0,
        }

        for date_, times in daily_data.items():
            per_day_outages_count = len(times)
            total_count += per_day_outages_count

            weekday = date.fromisoformat(date_).weekday()
            weekday_count[WEEKDAYS[weekday]] += per_day_outages_count

            for outage_start, _ in times:
                if "00:00:00" <= outage_start <= "06:00:00":
                    key = "00:00 - 06:00"
                elif "06:00:01" <= outage_start <= "12:00:00":
                    key = "06:01 - 12:00"
                elif "12:00:01" <= outage_start <= "18:00:00":
                    key = "12:01 - 18:00"
                elif "18:00:01" <= outage_start:
                    key = "18:01 - 23:59"

                time_ranges[key] += 1

        per_year_outages_agg[year] = {
            "counts": {
                "Počet výpadkov": total_count,
                "Počet dní": len(daily_data),
            },
            "time_ranges": time_ranges,
            "weekday_count": {k: v for k, v in weekday_count.items() if v},
        }

    now = datetime.now()
    return render_template(
        "index.html",
        per_year_outages=per_year_outages,
        per_year_outages_agg=per_year_outages_agg,
        current_year=now.year,
        updated_at=now.isoformat(" ", "minutes"),
    )


if __name__ == "__main__":
    app.run(debug=True)
