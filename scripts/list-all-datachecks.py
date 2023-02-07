from argparse import ArgumentParser

import numpy as np
import pandas as pd

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

    with open(args.output_path, "w") as f:
        for night in sorted(np.unique(runs["Date directory"])):
            print(template.format(night=night), file=f)
