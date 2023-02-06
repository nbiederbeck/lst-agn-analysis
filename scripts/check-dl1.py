from argparse import ArgumentParser
from glob import glob

import pandas as pd

parser = ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")
args = parser.parse_args()

template = "/fefs/aswg/data/real/OSA/DL1DataCheck_LongTerm/v0.9/{night}/DL1_datacheck_{night}.h5"


def check_dl1(item):
    filename = template.format(night=item["Date directory"])
    print(filename)
    return True


if __name__ == "__main__":
    # set up dataframe
    df = pd.read_csv(args.input_file)
    df["Result"] = False
    df["Reason"] = ""

    for idx, item in df.iterrows():
        df.loc[idx, "Result"] = check_dl1(item)

    df.to_csv(args.output_file, index=False)
