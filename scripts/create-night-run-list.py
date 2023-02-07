from argparse import ArgumentParser

import pandas as pd

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_path")
args = parser.parse_args()

assert args.output_path.endswith(".py"), "Output file must be a python file."

if __name__ == "__main__":
    df = pd.read_csv(args.input_path)

    runs = {}

    for night, group in df.groupby("Date directory"):
        runs[night] = set(group["Run ID"])

    with open(args.output_path, "w") as f:
        print("runs =", runs, file=f)
