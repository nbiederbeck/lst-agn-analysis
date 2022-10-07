from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets
from matplotlib import pyplot as plt


def main(output):
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.datasets = Datasets.read("build/datasets.fits.gz")

    analysis.read_models("build/model-best-fit.yaml")

    analysis.get_light_curve()

    fig, ax = plt.subplots()
    analysis.light_curve.plot(ax=ax, axis_name="time")
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
