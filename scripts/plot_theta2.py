from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--preliminary", action="store_true")
args = parser.parse_args()


import numpy as np
from astropy.table import Table
from gammapy.maps import MapAxis
from matplotlib import pyplot as plt


def plot_theta_squared_table(table, *, preliminary=False, ylim=None):
    theta2_axis = MapAxis.from_bounds(
        min(table["theta2_min"]),
        max(table["theta2_max"]),
        nbin=len(table["theta2_max"]),
        unit=table["theta2_max"].unit,
    )

    x = theta2_axis.center
    xerr = theta2_axis.bin_width

    on = table["counts"]
    off = table["counts_off"]

    fig, ax = plt.subplots()

    ax.errorbar(
        x,
        on,
        xerr=xerr / 2,
        yerr=np.sqrt(on),
        ls="",
        label="On",
        zorder=99,
    )
    ax.bar(
        x,
        off,
        width=xerr,
        color="gray",
        alpha=0.2,
    )
    ax.errorbar(
        x,
        off,
        xerr=xerr / 2,
        yerr=np.sqrt(off),
        ls="",
        label="Off",
    )

    if ylim is None:
        ymin = min(min(on), min(off))
        ymax = max(max(on), max(off))
        ylim = (0.9 * ymin, 1.1 * ymax)
    ax.set_ylim(ylim)
    ax.set_xlim(min(table["theta2_min"]), max(table["theta2_max"]))

    ax.legend(loc="upper right")
    ax.set_xlabel(r"$\theta^2 \:\:/\:\: \mathrm{deg}^2$")
    ax.set_ylabel("Counts")

    if preliminary:
        ax.annotate(
            "PRELIMINARY",
            (1, 0.68),
            xycoords="axes fraction",
            horizontalalignment="right",
            fontsize="larger",
            color="gray",
        )

    return fig, ax


def main(input_path, output, preliminary):
    table = Table.read(input_path)
    fig, ax = plot_theta_squared_table(table, preliminary=preliminary)
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
