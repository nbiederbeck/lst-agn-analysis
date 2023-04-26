from argparse import ArgumentParser

import numpy as np
import pandas as pd
from astropy.time import Time
from config import Config

parser = ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()

config = Config.parse_file(args.config)

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
    df["Run ID"] = df["Run ID"].apply("{:05d}".format)

    # select runs
    mask_source = df["Source name"] == config.source

    run_start = Time(df["Run start [UTC]"])
    mask_time = (config.time_start < run_start) & (run_start < config.time_stop)

    mask = mask_source & mask_time

    df[mask].to_csv(args.output_file, index=False)
