import json
from argparse import ArgumentParser

import pandas as pd
from config import Config

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_path")
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()

config = Config.parse_file(args.config)


def main():
    df = pd.read_csv(args.input_path, dtype={"Run ID": str})

    runs = {}

    for night, group in df.groupby("Date directory"):
        runs[night] = sorted(list(group["Run ID"]))

    with open(args.output_path, "w") as f:
        json.dump(runs, f)


if __name__ == "__main__":
    main()
