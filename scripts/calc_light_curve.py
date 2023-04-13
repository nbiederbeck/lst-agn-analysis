from argparse import ArgumentParser

from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets

parser = ArgumentParser()
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--dataset-path", required=True)
parser.add_argument("--best-model-path", required=True)
args = parser.parse_args()


def main(config, dataset_path, best_model_path, output):
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    # No explicit stacking here to get the per-run light-curve
    analysis.datasets = Datasets.read(dataset_path)

    analysis.read_models(best_model_path)

    analysis.get_light_curve()

    analysis.light_curve.write(
        output,
        format="lightcurve",
        overwrite=True,
    )


if __name__ == "__main__":
    main(**vars(args))
