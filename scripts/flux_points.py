from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets
from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt


def main(output):
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)

    analysis.datasets = Datasets.read("build/datasets.fits.gz")

    analysis.read_models("build/model-best-fit.yaml")

    analysis.get_flux_points()

    filename = "build/flux-points.fits.gz"

    analysis.flux_points.write(filename, overwrite=True)

    flux_points = FluxPoints.read(filename)

    flux_points.plot()

    fig, axes = plt.subplots(
        nrows=2, sharex=True, gridspec_kw=dict(height_ratios=[3, 1], hspace=0)
    )
    analysis.flux_points.plot_fit(*axes)

    axes[0].set_xlabel("")
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))