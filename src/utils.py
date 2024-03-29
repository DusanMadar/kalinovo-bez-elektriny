import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List

import requests


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


def build_downtime_data(
    log_dir_path: str, log_file_pattern: str, kind: str = "system"
) -> bool:
    downtime_data = defaultdict(list)

    for log_file in get_log_files(log_dir_path, log_file_pattern):
        data = extract_downtime_data(log_file, kind)
        if not data:
            continue

        for from_, to_ in data:
            downtime_data[from_.date().isoformat()].append(
                [from_.time().isoformat(), to_.time().isoformat()]
            )
    response = requests.get(
        "https://raw.githubusercontent.com/DusanMadar/kalinovo-bez-elektriny/master/data.json"  # noqa
    )
    if response.status_code != 200:
        raise ValueError("Failed to get existing data")

    local_down_time_data_hash = hashlib.md5(
        json.dumps(downtime_data, sort_keys=True, indent=2).encode("utf-8")
    ).hexdigest()
    response_downtime_data_hash = hashlib.md5(
        json.dumps(response.json(), sort_keys=True, indent=2).encode("utf-8")
    ).hexdigest()
    if local_down_time_data_hash != response_downtime_data_hash:
        data_file_path = Path(__file__).parent.parent.absolute().joinpath("data.json")
        with open(data_file_path, "w+") as fd:
            downtime_data = dict(
                sorted(downtime_data.items(), key=lambda x: x[0].lower(), reverse=True)
            )
            json.dump(downtime_data, fd, indent=4)

        return True

    return False
