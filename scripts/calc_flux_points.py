from argparse import ArgumentParser

from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--dataset-path", required=True)
parser.add_argument("--best-model-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(config, dataset_path, best_model_path, output):
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)

    datasets = Datasets.read(dataset_path)
    # Since we read the datasets here, they need not to be stacked
    # Especially our helper script to handle energy-dependent theta-cuts
    # does not stack at all.
    # This is helpful to still have per-run information, but means
    # we need to explicitly stack here, which should be cheap
    if config.datasets.stack:
        analysis.datasets = Datasets([datasets.stack_reduce()])
    else:
        analysis.datasets = datasets

    analysis.read_models(best_model_path)

    analysis.get_flux_points()

    analysis.flux_points.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
