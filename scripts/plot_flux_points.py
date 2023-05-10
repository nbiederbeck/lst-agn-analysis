from argparse import ArgumentParser

import numpy as np
from gammapy.datasets import FluxPointsDataset
from gammapy.modeling.models import Models
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("--best-model-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, best_model_path, output):
    flux_points = FluxPointsDataset.read(input_path)
    flux_points.models = Models.read(best_model_path)

    # See plot_light_curve.py for why this is necessary
    sed_type = flux_points.data.sed_type_plot_default
    y = getattr(flux_points.data, sed_type)
    y_errn, y_errp = flux_points.data._plot_get_flux_err(sed_type=sed_type)
    if np.any(~np.isnan(y)) or np.any(~np.isnan(y_errn)) or np.any(~np.isnan(y_errp)):
        # If everything is an upper limit, residuals will be all nan
        # This will fail because gammapy sets the yaxis limit in the
        # residual plot based on the max residual, so we need at least one
        # We can still plot the spectrum and flux points otherwise
        if np.any(~flux_points.data.is_ul.data.flatten()):
            fig, axes = plt.subplots(
                nrows=2,
                sharex=True,
                gridspec_kw=dict(height_ratios=[3, 1], hspace=0),
            )
            flux_points.plot_fit(*axes)
            axes[0].set_xlabel("")
        else:
            fig, ax = plt.subplots()
            flux_points.plot_spectrum(ax=ax)
    else:
        # Need an empty plot to satisfy the rule
        fig, ax = plt.subplots()

    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
