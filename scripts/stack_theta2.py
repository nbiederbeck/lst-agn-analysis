from argparse import ArgumentParser

import numpy as np
from astropy.io import fits
from astropy.table import Table
from gammapy.stats import WStatCountsStatistic
from gammapy.utils import pbar

parser = ArgumentParser()
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-i", "--input-files", required=True, nargs="+")
args = parser.parse_args()

pbar.SHOW_PROGRESS_BAR = True


def create_empty_table(theta_squared_axis, position):
    table = Table()
    table["theta2_min"] = theta_squared_axis.edges_min
    table["theta2_max"] = theta_squared_axis.edges_max
    table["counts"] = 0
    table["counts_off"] = 0
    table["acceptance"] = 0.0
    table["acceptance_off"] = 0.0
    table.meta["NON_THR"] = 0
    table.meta["NOFF_THR"] = 0
    table.meta["ON_RA"] = position.icrs.ra
    table.meta["ON_DEC"] = position.icrs.dec
    return table


def add_stats(table):
    stat = WStatCountsStatistic(table["counts"], table["counts_off"], table["alpha"])
    table["excess"] = stat.n_sig
    table["sqrt_ts"] = stat.sqrt_ts
    table["excess_errn"] = stat.compute_errn()
    table["excess_errp"] = stat.compute_errp()
    return table


def main(input_files, output):  # noqa: PLR0915
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
