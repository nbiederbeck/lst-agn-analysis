from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from astropy.table import Table

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_directory")
args = parser.parse_args()

outdir = Path(args.output_directory)


def to_num(n: int) -> str:
    return r"\num{" + str(n) + "}"


def main():
    tbl = Table.read("build/dl1-datachecks-masked.h5")

    mask_source = tbl["mask_run_id"]
    mask_time_pedestal_pointing = tbl["mask_run_selection"]
    mask_ped_charge = tbl["mask_pedestal_charge"]
    mask_cosmics = mask_ped_charge & tbl["mask_cosmics"] & tbl["mask_cosmics_above"]

    with open(outdir / "runselection-01-observing-source.tex", "w") as f:
        f.write(to_num(np.count_nonzero(mask_source)))

    with open(outdir / "runselection-02-ok-during-timeframe.tex", "w") as f:
        f.write(to_num(np.count_nonzero(mask_time_pedestal_pointing)))

    with open(outdir / "runselection-03-pedestal-charge.tex", "w") as f:
        f.write(to_num(np.count_nonzero(mask_ped_charge)))

    with open(outdir / "runselection-04-cosmics.tex", "w") as f:
        f.write(to_num(np.count_nonzero(mask_cosmics)))


if __name__ == "__main__":
    main()
