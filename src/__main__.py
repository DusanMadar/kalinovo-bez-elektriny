import argparse

from src import freeze
from src.utils import build_downtime_data


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir-path", required=True, help="absolute path")
    parser.add_argument("--log-file-pattern", required=True)
    return parser


def main() -> None:
    parser = get_arg_parser()
    args = parser.parse_args()

    if build_downtime_data(args.log_dir_path, args.log_file_pattern):
        freeze.main()


if __name__ == "__main__":
    main()
