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


def main():
    runs = pd.read_csv(args.input_path)

    filenames = [
        template.format(night=night)
        for night in sorted(np.unique(runs["Date directory"]))
    ]

    tables = [
        read_table(filename, "/runsummary/table")
        for filename in track(filenames)
        if Path(filename).exists()
    ]

    if len(tables) == 0:
        p = Path(args.output_path)
        if not p.exists():
            raise ValueError("Output path does not exist and no files to merge.")
        p.touch()
        return

    runsummary = vstack(
        tables,
        metadata_conflicts="silent",
    )

    runsummary.write(
        args.output_path,
        serialize_meta=True,
        overwrite=True,
        path="data",
        compression=True,
    )


if __name__ == "__main__":
    main()
