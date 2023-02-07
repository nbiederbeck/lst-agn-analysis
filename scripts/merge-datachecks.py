from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.table import vstack
from ctapipe.io import read_table
from rich.progress import track

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_path")
args = parser.parse_args()

template = (
    "/fefs/aswg/data/real/OSA/DL1DataCheck_LongTerm/"
    "v0.9/{night}/DL1_datacheck_{night}.h5"
)


if __name__ == "__main__":
    runs = pd.read_csv(args.input_path)

    filenames = [
        template.format(night=night)
        for night in sorted(np.unique(runs["Date directory"]))
    ]

    runsummary = vstack(
        [
            read_table(filename, "/runsummary/table")
            for filename in track(filenames)
            if Path(filename).exists()
        ],
        metadata_conflicts="silent",
    )

    runsummary.write(
        args.output_path,
        serialize_meta=True,
        overwrite=True,
        path="data",
        compression=True,
    )
