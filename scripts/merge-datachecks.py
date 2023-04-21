import logging
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.table import vstack
from ctapipe.io import read_table
from log import setup_logging
from rich.progress import track

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_path")
parser.add_argument("--log-file")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

template = (
    "/fefs/aswg/data/real/OSA/DL1DataCheck_LongTerm/"
    "v0.9/{night}/DL1_datacheck_{night}.h5"
)


def main():
    setup_logging(logfile=args.log_file, verbose=args.verbose)
    log = logging.getLogger("merge-datachecks")

    runs = pd.read_csv(args.input_path)

    filenames = [
        template.format(night=night)
        for night in sorted(np.unique(runs["Date directory"]))
    ]

    datachecks = []
    for f in filenames:
        if Path(f).exists():
            datachecks.append(f)
        else:
            log.warning("%s not found.", f)

    if len(datachecks) == 0:
        raise Exception(
            "No datachecks exist. "
            "That might come from a bad configuration or "
            "means that none are found. "
            "Please check the logs.",
        )

    tables = [read_table(d, "/runsummary/table") for d in track(datachecks)]

    runsummary = vstack(
        tables,
        metadata_conflicts="silent",
    )

    runsummary["mean_ra"].unit = u.deg
    runsummary["mean_dec"].unit = u.deg
    runsummary["elapsed_time"].unit = u.s

    runsummary["cosmics_rate"] = runsummary["num_cosmics"] / runsummary["elapsed_time"]
    runsummary["cosmics_rate_above10"] = (
        runsummary["cosmics_rate"] * runsummary["cosmics_fraction_pulses_above10"]
    )
    runsummary["cosmics_rate_above30"] = (
        runsummary["cosmics_rate"] * runsummary["cosmics_fraction_pulses_above30"]
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
