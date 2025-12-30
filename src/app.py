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

WEEKDAYS = [
    "Pondelok",
    "Utorok",
    "Streda",
    "Štvrtok",
    "Piatok",
    "Sobota",
    "Nedeľa",
]
MONTHS = [
    "Január",
    "Február",
    "Marec",
    "Apríl",
    "Máj",
    "Jún",
    "Júl",
    "August",
    "September",
    "Október",
    "November",
    "December",
]


@app.route("/")
def index():
    data = csv_to_dict()

    outages_by_year_and_day = defaultdict(dict)
    outages_by_year_and_month = defaultdict(lambda: defaultdict(int))
    for date_, daily_data in data.items():
        date_parts = date_.split("-")
        year = int(date_parts[0])
        month = int(date_parts[1])

        # Not enough data before 2022.
        if year < 2022:
            continue

        outages_by_year_and_day[year][date_] = daily_data
        outages_by_year_and_month[year][month] += len(daily_data)

    outages_by_year_and_day_agg = {}
    for year, daily_data in outages_by_year_and_day.items():
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

        outages_by_year_and_day_agg[year] = {
            "counts": {
                "Počet výpadkov": total_count,
                "Počet dní": len(daily_data),
            },
            "time_ranges": time_ranges,
            "weekday_count": {k: v for k, v in weekday_count.items() if v},
        }

    # Prepare chart data with separate datasets per year
    monthly_by_year_chart = {"labels": MONTHS, "datasets": []}

    years = sorted(outages_by_year_and_month.keys())

    for year in years:
        year_data = outages_by_year_and_month[year]
        # Create array with data for all 12 months (0 if no data)
        data_for_year = [year_data.get(month, 0) for month in range(1, 13)]

        monthly_by_year_chart["datasets"].append({
            "label": str(year),
            "data": data_for_year
        })

    years_for_yearly_chart = [y for y in sorted(outages_by_year_and_day_agg.keys())]
    yearly_totals_chart = {
        "labels": [str(year) for year in years_for_yearly_chart],
        "datasets": [{
            "label": "Počet výpadkov",
            "data": [outages_by_year_and_day_agg[year]["counts"]["Počet výpadkov"]
                     for year in years_for_yearly_chart]
        }]
    }

    # Chart 3: Daily (weekday) overview by year (2022+)
    daily_by_year_chart = {"labels": WEEKDAYS, "datasets": []}

    for year in sorted([y for y in outages_by_year_and_day_agg.keys()]):
        weekday_data = outages_by_year_and_day_agg[year]["weekday_count"]
        # Create array with data for all 7 weekdays (0 if no data)
        data_for_year = [weekday_data.get(weekday, 0) for weekday in WEEKDAYS]
        daily_by_year_chart["datasets"].append({
            "label": str(year),
            "data": data_for_year
        })

    # Chart 4: Hourly (time range) overview by year (2022+)
    time_range_labels = ["00:00 - 06:00", "06:01 - 12:00", "12:01 - 18:00", "18:01 - 23:59"]
    hourly_by_year_chart = {"labels": time_range_labels, "datasets": []}

    for year in sorted([y for y in outages_by_year_and_day_agg.keys()]):
        time_range_data = outages_by_year_and_day_agg[year]["time_ranges"]
        # Create array with data for all 4 time ranges
        data_for_year = [time_range_data.get(time_range, 0) for time_range in time_range_labels]
        hourly_by_year_chart["datasets"].append({
            "label": str(year),
            "data": data_for_year
        })

    now = datetime.now()

    return render_template(
        "index.html",
        outages_by_year_and_day=outages_by_year_and_day,
        outages_by_year_and_day_agg=outages_by_year_and_day_agg,
        monthly_by_year_chart=monthly_by_year_chart,
        yearly_totals_chart=yearly_totals_chart,
        daily_by_year_chart=daily_by_year_chart,
        hourly_by_year_chart=hourly_by_year_chart,
        current_year=now.year,
        updated_at=now.isoformat(" ", "minutes"),
    )


if __name__ == "__main__":
    app.run(debug=True)
