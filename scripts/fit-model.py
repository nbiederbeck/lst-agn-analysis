from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets


def main(output):
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.datasets = Datasets.read("build/datasets.fits.gz")

    analysis.read_models("configs/model_config.yaml")

    analysis.run_fit()
    analysis.models.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
