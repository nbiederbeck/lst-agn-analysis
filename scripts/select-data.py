from argparse import ArgumentParser

import numpy as np
import pandas as pd

parser = ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")
parser.add_argument("source_name")
args = parser.parse_args()

if __name__ == "__main__":
    tables = pd.read_html(args.input_file)

    df = tables[0]  # only one table

    # sanitize input
    df["Date directory"] = np.char.replace(
        np.array(df["Date directory"], dtype=str),
        "-",
        "",
    ).astype(int)
    df["Run start [UTC]"] = np.array(df["Run start [UTC]"], dtype=np.datetime64)

    mask = df["Source name"] == args.source_name
    assert mask.sum() > 0, f"Source name `{args.source_name}` not found."
    df[mask].to_csv(args.output_file, index=False)
