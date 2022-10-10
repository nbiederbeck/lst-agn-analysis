from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("--model-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.datasets import FluxPointsDataset
from gammapy.modeling.models import Models
from matplotlib import pyplot as plt


def main(input_path, model_path, output):
    flux_points = FluxPointsDataset.read(input_path)
    flux_points.models = Models.read(model_path)

    fig, axes = plt.subplots(
        nrows=2,
        sharex=True,
        gridspec_kw=dict(height_ratios=[3, 1], hspace=0),
    )
    flux_points.plot_fit(*axes)

    axes[0].set_xlabel("")
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
