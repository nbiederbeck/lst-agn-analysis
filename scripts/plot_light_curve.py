from argparse import ArgumentParser

import numpy as np
from astropy.table import Table
from astropy.time import Time
from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt
from matplotlib.dates import ConciseDateFormatter

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--blocks", required=False)
args = parser.parse_args()


def main(input_path, output, blocks):
    lc = FluxPoints.read(input_path, format="lightcurve")

    fig, ax = plt.subplots()
    # This also happens in the plot call, but this way we can
    # fail early if there is no positive data (the source is not detected)
    # gammapy does not handle that case, so the script would just fail
    # Alternatively one could just set up an exception, but I think it is
    # fine to special-case the scenario of "no data to plot"
    sed_type = lc.sed_type_plot_default
    y = getattr(lc, sed_type)
    y_errn, y_errp = lc._plot_get_flux_err(sed_type=sed_type)

    # This might be a bit overkill
    if np.any(~np.isnan(y)) or np.any(~np.isnan(y_errn)) or np.any(~np.isnan(y_errp)):
        lc.plot(ax=ax, sed_type=sed_type)
        if blocks:
            t = Table.read(blocks)
            for start, stop in zip(t["start"], t["stop"]):
                ax.axvline(
                    Time(start, format="mjd").to_datetime(),
                    color="k",
                    linestyle="dashed",
                )

            ax.axvline(
                Time(stop, format="mjd").to_datetime(),
                color="k",
                linestyle="dashed",
                label="bayesian blocks",
            )

    ax.set_xlabel("Date")
    ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.legend()
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
