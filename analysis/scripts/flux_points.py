from analysis import get_analysis
from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt


def main():
    analysis = get_analysis()
    analysis.get_datasets()

    analysis.read_models("build/model-best-fit.yaml")

    analysis.get_flux_points()

    filename = "build/flux-points.fits.gz"

    analysis.flux_points.write(filename)

    flux_points = FluxPoints.read(filename)

    flux_points.plot()

    fig, axes = plt.subplots(
        nrows=2, sharex=True, gridspec_kw=dict(height_ratios=[3, 1], hspace=0)
    )
    analysis.flux_points.plot_fit(*axes)

    axes[0].set_xlabel("")
    fig.savefig("build/flux_points.pdf")
