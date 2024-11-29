import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List

import requests

CSV_DATA_PATH = Path(__file__).parent.parent.absolute().joinpath("data.csv")


def csv_to_dict() -> dict[str, list[list[str]]]:
    data = defaultdict(list)

    with open(CSV_DATA_PATH, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data[row["date"]].append([row["start_time"], row["end_time"]])

    return data


def dict_to_csv(data: dict[str, list[list[str]]]) -> None:
    with open(CSV_DATA_PATH, "w", newline="") as csv_file:
        fieldnames = ["date", "start_time", "end_time"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for date_, periods in data.items():
            for period in periods:
                writer.writerow(
                    {"date": date_, "start_time": period[0], "end_time": period[1]}
                )


def get_log_files(log_dir_path: str, log_file_pattern: str) -> List[str]:
    return [
        str(item.absolute())
        for item in Path(log_dir_path).glob("**/*")
        if item.is_file() and log_file_pattern in item.name
    ]


def extract_downtime_data(log_file_path: str, kind: str) -> List[List[datetime]]:
    with open(log_file_path) as fd:
        records = [line.strip().split(" ") for line in fd.readlines()]
        return [
            [datetime.fromisoformat(record[4]), datetime.fromisoformat(record[6])]
            for record in records
            if record[1] == kind
        ]


def get_public_data() -> dict[str, set[tuple[str, str]]]:
    response = requests.get(
        "https://raw.githubusercontent.com/DusanMadar/kalinovo-bez-elektriny/master/data.csv"  # noqa
    )
    if response.status_code != 200:
        raise ValueError("Failed to get existing data")

    data = defaultdict(set)

    csv_content = response.content.decode("utf-8")
    csv_reader = csv.DictReader(csv_content.splitlines())
    for row in csv_reader:
        # # Simulate missing data for local testing.
        # # Data from sample_logs/downtime.log.
        # if row["date"] == "2023-02-18" and row["start_time"] == "04:13:13":
        #     continue
        data[row["date"]].add((row["start_time"], row["end_time"]))

    return data


def collect_downtime_data(
    log_dir_path: str, log_file_pattern: str, kind: str
) -> dict[str, list[tuple[str, str]]]:
    downtime_data = defaultdict(list)

    for log_file in get_log_files(log_dir_path, log_file_pattern):
        data = extract_downtime_data(log_file, kind)
        if not data:
            continue

        for from_, to_ in data:
            downtime_data[from_.date().isoformat()].append(
                (from_.time().isoformat(), to_.time().isoformat())
            )

    return downtime_data


def downtime_data_updated(
    log_dir_path: str, log_file_pattern: str, kind: str = "system"
) -> bool:
    data_updated = False

    downtime_data = collect_downtime_data(log_dir_path, log_file_pattern, kind)
    public_data = get_public_data()

    for date_, outage_periods in downtime_data.items():
        published_outage_periods = public_data.get(date_)
        if published_outage_periods:
            for outage_period in outage_periods:
                if outage_period not in published_outage_periods:
                    public_data[date_].add(outage_period)
                    data_updated = True
        else:
            public_data[date_] = set(outage_periods)
            data_updated = True

    if data_updated:
        sorted_data = {}
        for date_ in sorted(public_data.keys(), reverse=True):
            outage_periods = sorted(public_data[date_], key=lambda period: period[0])
            sorted_data[date_] = outage_periods

        dict_to_csv(sorted_data)

    return data_updated
