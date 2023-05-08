from argparse import ArgumentParser

import numpy as np
from gammapy.datasets import FluxPointsDataset
from gammapy.modeling.models import Models
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("--models", required=True, nargs="+")
parser.add_argument("--flux-points", required=True, nargs="+")
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(models, flux_points, output):
    # Should this be configurable?
    # get cm from matplotlibrc?
    colors = plt.cm.Spectral(np.linspace(0, 1, len(models)))

    fig, ax = plt.subplots()

    # only plot the model maybe?
    # plot pairs/triples of flux points?
    for i, (model_path, flux_points_path, color) in enumerate(
        zip(models, flux_points, colors),
    ):
        fp = FluxPointsDataset.read(flux_points_path)
        fp.models = Models.read(model_path)
        fp.plot_spectrum(
            ax=ax,
            kwargs_fp={"color": color, "label": "", "alpha": 0.3},
            kwargs_model={"color": color, "label": f"Block {i}"},
        )

    ax.legend()
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
