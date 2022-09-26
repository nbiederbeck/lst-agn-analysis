from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt


def main():
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.get_observations()
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

if __name__ == "__main__":
    main()
