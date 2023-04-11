from argparse import ArgumentParser

import numpy as np
from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt
from matplotlib.dates import ConciseDateFormatter

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, output):
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
    if (
        np.count_nonzero(~np.isnan(y) > 0)
        or np.count_nonzero(~np.isnan(y_errn) > 0)
        or np.count_nonzero(~np.isnan(y_errp) > 0)
    ):
        lc.plot(ax=ax, sed_type=sed_type)

    #    ax.set_ylabel(
    #        r"$\Phi \:\:/\:\: "
    #        + r"\si{\per\centi\meter\squared\per\second\per\tera\electronvolt}$",
    #    )
    ax.set_xlabel("Date")
    ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
