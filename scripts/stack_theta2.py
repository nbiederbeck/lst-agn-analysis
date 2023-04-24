import logging
from argparse import ArgumentParser

import numpy as np
from astropy.io import fits
from astropy.table import Table
from calc_theta2_per_obs import add_stats
from gammapy.utils import pbar
from log import setup_logging

parser = ArgumentParser()
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-i", "--input-files", required=True, nargs="+")
parser.add_argument("--log-file")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

pbar.SHOW_PROGRESS_BAR = True


def main(input_files, output, log_file, verbose):  # noqa: PLR0915
    setup_logging(logfile=log_file, verbose=verbose)
    logging.getLogger("theta2-stacking")
    stacked_tables = []
    livetime_tot = 0

    hdulist = [fits.PrimaryHDU()]
    for i, path in enumerate(input_files):
        with fits.open(path) as f:
            if i == 0:
                n_bins = len(f) - 1
                stacked_tables = [Table.read(hdu).copy() for hdu in f[1:]]
                n_rows = len(stacked_tables[-1])
                alpha_tot = np.zeros(n_rows)
            else:
                n = len(f) - 1
                assert (
                    n_bins == n
                ), f"not all files have the same length. expected {n_bins}, git {n}"
                for hdu, stacked in zip(f[1:], stacked_tables):
                    table = Table.read(hdu)
                    for c in ["counts", "counts_off", "acceptance", "acceptance_off"]:
                        stacked[c] += table[c]
                alpha = table["acceptance"] / table["acceptance_off"]
                alpha_tot += alpha * table.meta["TOBS"]
                livetime_tot += table.meta["TOBS"]

    for t in stacked_tables:
        table = add_stats(t)
        table["alpha"] = alpha_tot / livetime_tot
        hdulist.append(fits.table_to_hdu(t))
    fits.HDUList(hdulist).writeto(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
